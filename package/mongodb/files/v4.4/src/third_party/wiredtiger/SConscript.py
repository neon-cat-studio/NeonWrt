# -*- mode: python; -*-
import re
import textwrap

Import("env debugBuild")
Import("get_option")
Import("endian")

env = env.Clone()

env.InjectThirdParty(libraries=['snappy', 'zlib', 'zstd'])

if endian == "big":
    env.Append(CPPDEFINES=[('WORDS_BIGENDIAN', 1)])

env.Append(CPPPATH=[
        "src/include",
    ])

# Enable asserts in debug builds
if debugBuild:
    env.Append(CPPDEFINES=[
        "HAVE_DIAGNOSTIC",
        ])

# Enable optional rich logging
env.Append(CPPDEFINES=["HAVE_VERBOSE"])

conf = Configure(env)
if conf.CheckFunc("fallocate"):
    conf.env.Append(CPPDEFINES=[
        "HAVE_FALLOCATE"
    ])
if conf.CheckFunc("sync_file_range"):
    conf.env.Append(CPPDEFINES=[
        "HAVE_SYNC_FILE_RANGE"
    ])

# GCC 8+ includes x86intrin.h in non-x64 versions of the compiler so limit the check to x64.
if env['TARGET_ARCH'] == 'x86_64' and conf.CheckCHeader('x86intrin.h'):
    conf.env.Append(CPPDEFINES=[
        "HAVE_X86INTRIN_H"
    ])
if conf.CheckCHeader('arm_neon.h'):
    conf.env.Append(CPPDEFINES=[
        "HAVE_ARM_NEON_INTRIN_H"
    ])
env = conf.Finish();

env.Append(CPPPATH=["build_linux"])
env.Append(CPPDEFINES=["_GNU_SOURCE"])

useZlib = True
useSnappy = True
useZstd = True

version_file = 'build_posix/aclocal/version-set.m4'

VERSION_MAJOR = None
VERSION_MINOR = None
VERSION_PATCH = None
VERSION_STRING = None

# Read the version information from the version-set.m4 file
for l in open(File(version_file).srcnode().abspath):
    if re.match(r'^VERSION_[A-Z]+', l):
        exec(l)

if (VERSION_MAJOR == None or
    VERSION_MINOR == None or
    VERSION_PATCH == None or
    VERSION_STRING == None):
    print("Failed to find version variables in " + version_file)
    Exit(1)

wiredtiger_includes = """
        #include <sys/types.h>
        #ifndef _WIN32
        #include <inttypes.h>
        #endif
        #include <stdarg.h>
        #include <stdbool.h>
        #include <stdint.h>
        #include <stdio.h>
    """
wiredtiger_includes = textwrap.dedent(wiredtiger_includes)
replacements = {
    '@VERSION_MAJOR@' : VERSION_MAJOR,
    '@VERSION_MINOR@' : VERSION_MINOR,
    '@VERSION_PATCH@' : VERSION_PATCH,
    '@VERSION_STRING@' : VERSION_STRING,
    '@uintmax_t_decl@': "",
    '@uintptr_t_decl@': "",
    '@off_t_decl@' : "typedef off_t wt_off_t;",
    '@wiredtiger_includes_decl@': wiredtiger_includes
}

env.Substfile(
    target='wiredtiger.h',
    source=[
        'src/include/wiredtiger.in',
    ],
    SUBST_DICT=replacements)

env.Install(
    target='.',
    source=[
        'src/include/wiredtiger_ext.h'
    ],
)

env.Alias('generated-sources', "wiredtiger.h")
env.Alias('generated-sources', "wiredtiger_ext.h")

#
# WiredTiger library
#
# Map WiredTiger build conditions: any conditions that appear in WiredTiger's
# dist/filelist must appear here, and if the value is true, those files will be
# included.
#
condition_map = {
    'POSIX_HOST'   : True,
    'WINDOWS_HOST' : False,

    'ARM64_HOST'   : env['TARGET_ARCH'] == 'aarch64',
    'POWERPC_HOST' : env['TARGET_ARCH'] == 'ppc64le',
    'X86_HOST'     : env['TARGET_ARCH'] == 'x86_64',
    'ZSERIES_HOST' : env['TARGET_ARCH'] == 's390x',
}

def filtered_filelist(f, checksum):
    for line in f:
        file_cond = line.split()
        if line.startswith("#") or len(file_cond) == 0:
            continue
        if len(file_cond) == 1 or condition_map.get(file_cond[1], False):
            if line.startswith('src/checksum/') == checksum:
                yield file_cond[0]

filelistfile = 'dist/filelist'
with open(File(filelistfile).srcnode().abspath) as filelist:
    wtsources = list(filtered_filelist(filelist, False))

with open(File(filelistfile).srcnode().abspath) as filelist:
    cssources = list(filtered_filelist(filelist, True))

if useZlib:
    env.Append(CPPDEFINES=['HAVE_BUILTIN_EXTENSION_ZLIB'])
    wtsources.append("ext/compressors/zlib/zlib_compress.c")

if useSnappy:
    env.Append(CPPDEFINES=['HAVE_BUILTIN_EXTENSION_SNAPPY'])
    wtsources.append("ext/compressors/snappy/snappy_compress.c")

if useZstd:
    env.Append(CPPDEFINES=['HAVE_BUILTIN_EXTENSION_ZSTD'])
    wtsources.append("ext/compressors/zstd/zstd_compress.c")

# Use hardware by default on all platforms if available.
# If not available at runtime, we fall back to software in some cases.
if (get_option("use-hardware-crc32") == "off"):
    env.Append(CPPDEFINES=["HAVE_NO_CRC32_HARDWARE"])

cslib = env.Library(
    target="wiredtiger_checksum",
    source=cssources,
)

wtlib = env.Library(
    target="wiredtiger",
    source=wtsources,
    LIBDEPS=[
        'wiredtiger_checksum',
        '$BUILD_DIR/third_party/shim_allocator',
        '$BUILD_DIR/third_party/shim_snappy',
        '$BUILD_DIR/third_party/shim_zlib',
        '$BUILD_DIR/third_party/shim_zstd',
    ],
    LIBDEPS_TAGS=[
        'init-no-global-side-effects',
    ],
)

env.Depends([cslib, wtlib], [filelistfile, version_file])

wtbinEnv = env.Clone()

wtbin = wtbinEnv.Program(
    target="wt",
    source=Glob("src/utilities/*.c"),
    LIBDEPS=["wiredtiger"],
    # SCons's smart_link() decides to try and link as C because all of the file extensions are .c;
    # however, we must link with snappy, etc. as C++. The smart_link() function isn't used by
    # default on Windows, so we leave the value unchanged on other platforms.
    LINK="$CXX" if wtbinEnv["LINK"] == "$SMARTLINK" else wtbinEnv["LINK"],
    AIB_COMPONENT="dist-test",
)

hygienic = get_option('install-mode') == 'hygienic'
if not hygienic:
    wtbin_install = wtbinEnv.Install("#/", wtbin)
    wtbinEnv.Alias("tools", wtbin_install)
