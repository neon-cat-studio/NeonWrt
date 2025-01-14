# -*- mode: python; -*-
# build file for MongoDB
# this requires scons
# you can get from http://www.scons.org
# then just type scons

# some common tasks
#   build 64-bit mac and pushing to s3
#      scons --64 s3dist
#      scons --distname=0.8 s3dist
#      all s3 pushes require settings.py and simples3

# This file, SConstruct, configures the build environment, and then delegates to
# several, subordinate SConscript files, which describe specific build rules.

import buildscripts
import copy
import datetime
import imp
import errno
import json
import os
import re
import shlex
import shutil
import stat
import sys
import textwrap
import types
import urllib
import urllib2
import uuid
from buildscripts import utils
from buildscripts import moduleconfig

import libdeps

EnsureSConsVersion( 2, 3, 0 )

def findSettingsSetup():
    sys.path.append( "." )
    sys.path.append( ".." )
    sys.path.append( "../../" )

def versiontuple(v):
    return tuple(map(int, (v.split("."))))

# --- options ----
options = {}

def add_option( name, help, nargs, contributesToVariantDir,
                dest=None, default = None, type="string", choices=None, metavar=None, const=None ):

    if dest is None:
        dest = name

    if type == 'choice' and not metavar:
        metavar = '[' + '|'.join(choices) + ']'

    AddOption( "--" + name , 
               dest=dest,
               type=type,
               nargs=nargs,
               action="store",
               choices=choices,
               default=default,
               metavar=metavar,
               const=const,
               help=help )

    options[name] = { "help" : help ,
                      "nargs" : nargs ,
                      "contributesToVariantDir" : contributesToVariantDir ,
                      "dest" : dest,
                      "default": default }

def get_option( name ):
    return GetOption( name )

def has_option( name ):
    x = get_option( name )
    if x is None:
        return False

    if x == False:
        return False

    if x == "":
        return False

    return True

def get_variant_dir():

    build_dir = get_option('build-dir').rstrip('/')

    if has_option('variant-dir'):
        return (build_dir + '/' + get_option('variant-dir')).rstrip('/')

    substitute = lambda x: re.sub( "[:,\\\\/]" , "_" , x )

    a = []

    for name in options:
        o = options[name]
        if not has_option( o["dest"] ):
            continue
        if not o["contributesToVariantDir"]:
            continue
        if get_option(o["dest"]) == o["default"]:
            continue

        if o["nargs"] == 0:
            a.append( name )
        else:
            x = substitute( get_option( name ) )
            a.append( name + "_" + x )

    extras = []
    if has_option("extra-variant-dirs"):
        extras = [substitute(x) for x in get_option( 'extra-variant-dirs' ).split( ',' )]

    if has_option("add-branch-to-variant-dir"):
        extras += ["branch_" + substitute( utils.getGitBranch() )]

    if has_option('cache'):
        s = "cached"
        s += "/".join(extras) + "/"
    else:
        s = "${PYSYSPLATFORM}/"
        a += extras

        if len(a) > 0:
            a.sort()
            s += "/".join( a ) + "/"
        else:
            s += "normal/"

    return (build_dir + '/' + s).rstrip('/')

# build output
add_option( "mute" , "do not display commandlines for compiling and linking, to reduce screen noise", 0, False )

# installation/packaging
add_option( "prefix" , "installation prefix" , 1 , False, default='$BUILD_ROOT/install' )
add_option( "distname" , "dist name (0.8.0)" , 1 , False )
add_option( "distmod", "additional piece for full dist name" , 1 , False )
add_option( "distarch", "override the architecture name in dist output" , 1 , False )
add_option( "nostrip", "do not strip installed binaries" , 0 , False )
add_option( "extra-variant-dirs", "extra variant dir components, separated by commas", 1, False)
add_option( "add-branch-to-variant-dir", "add current git branch to the variant dir", 0, False )
add_option( "build-dir", "build output directory", 1, False, default='#build')
add_option( "variant-dir", "override variant subdirectory", 1, False )
add_option( "staging-dir" , "openwrt toolchain staging directory" , 1 , False )

# linking options
add_option( "release" , "release build" , 0 , True )
add_option( "static" , "fully static build" , 0 , False )
add_option( "static-libstdc++" , "statically link libstdc++" , 0 , False )
add_option( "lto", "enable link time optimizations (experimental, except with MSVC)" , 0 , True )

# base compile flags
add_option( "64" , "whether to force 64 bit" , 0 , True , "force64" )
add_option( "32" , "whether to force 32 bit" , 0 , True , "force32" )

add_option( "endian" , "endianness of target platform" , 1 , False , "endian",
            type="choice", choices=["big", "little", "auto"], default="auto" )

add_option( "cxx", "compiler to use" , 1 , True )
add_option( "cc", "compiler to use for c" , 1 , True )
add_option( "cc-use-shell-environment", "use $CC from shell for C compiler" , 0 , False )
add_option( "cxx-use-shell-environment", "use $CXX from shell for C++ compiler" , 0 , False )
add_option( "ld", "linker to use" , 1 , True )
add_option( "c++11", "enable c++11 support (required as of 3.0.5)", "?", True,
            type="choice", choices=["on"], const="on", default="on" )
add_option( "disable-minimum-compiler-version-enforcement",
            "allow use of unsupported older compilers (NEVER for production builds)",
            0, False )

add_option( "cpppath", "Include path if you have headers in a nonstandard directory" , 1 , False )
add_option( "libpath", "Library path if you have libraries in a nonstandard directory" , 1 , False )

add_option( "extrapath", "comma separated list of add'l paths  (--extrapath /opt/foo/,/foo) static linking" , 1 , False )
add_option( "extrapathdyn", "comma separated list of add'l paths  (--extrapath /opt/foo/,/foo) dynamic linking" , 1 , False )
add_option( "extralib", "comma separated list of libraries  (--extralib js_static,readline" , 1 , False )

# experimental features
add_option( "mm", "use main memory instead of memory mapped files" , 0 , True )
add_option( "ssl" , "Enable SSL" , 0 , True )
add_option( "rocksdb" , "Enable RocksDB" , 0 , False )
add_option( "wiredtiger", "Enable wiredtiger", "?", True, "wiredtiger",
            type="choice", choices=["on", "off"], const="on", default="on")

# library choices
js_engine_choices = ['v8-3.12', 'v8-3.25', 'none']
add_option( "js-engine", "JavaScript scripting engine implementation", 1, False,
           type='choice', default=js_engine_choices[0], choices=js_engine_choices)
add_option( "libc++", "use libc++ (experimental, requires clang)", 0, True )

add_option( "use-glibcxx-debug",
            "Enable the glibc++ debug implementations of the C++ standard libary", 0, True )

# mongo feature options
add_option( "noshell", "don't build shell" , 0 , True )
add_option( "safeshell", "don't let shell scripts run programs (still, don't run untrusted scripts)" , 0 , True )
add_option( "win2008plus",
            "use newer operating system API features (deprecated, use win-version-min instead)" ,
            0 , False )

# dev options
add_option( "d", "debug build no optimization, etc..." , 0 , True , "debugBuild" )
add_option( "dd", "debug build no optimization, additional debug logging, etc..." , 0 , True , "debugBuildAndLogging" )

# new style debug and optimize flags
add_option( "dbg", "Enable runtime debugging checks", "?", True, "dbg",
            type="choice", choices=["on", "off"], const="on" )

add_option( "opt", "Enable compile-time optimization", "?", True, "opt",
            type="choice", choices=["on", "off"], const="on" )

add_option( "sanitize", "enable selected sanitizers", 1, True, metavar="san1,san2,...sanN" )
add_option( "llvm-symbolizer", "name of (or path to) the LLVM symbolizer", 1, False, default="llvm-symbolizer" )

add_option( "durableDefaultOn" , "have durable default to on" , 0 , True )
add_option( "durableDefaultOff" , "have durable default to off" , 0 , True )

add_option( "pch" , "use precompiled headers to speed up the build (experimental)" , 0 , True , "usePCH" )
add_option( "distcc" , "use distcc for distributing builds" , 0 , False )

add_option( "allocator" , "allocator to use (tcmalloc or system)" , 1 , True,
            default="tcmalloc" )
add_option( "gdbserver" , "build in gdb server support" , 0 , True )
add_option( "heapcheck", "link to heap-checking malloc-lib and look for memory leaks during tests" , 0 , False )
add_option( "gcov" , "compile with flags for gcov" , 0 , True )

add_option("smokedbprefix", "prefix to dbpath et al. for smoke tests", 1 , False )
add_option("smokeauth", "run smoke tests with --auth", 0 , False )

add_option("use-sasl-client", "Support SASL authentication in the client library", 0, False)

# library choices
boost_choices = ['1.49', '1.56']
add_option( "internal-boost", "Specify internal boost version to use", 1, True,
           type='choice', default=boost_choices[0], choices=boost_choices)

add_option( "system-boost-lib-search-suffixes",
            "Comma delimited sequence of boost library suffixes to search",
            1, False )

# deprecated
add_option( "use-new-tools" , "put new tools in the tarball", 0 , False )

add_option( "use-cpu-profiler",
            "Link against the google-perftools profiler library",
            0, False )

add_option('build-fast-and-loose', "looser dependency checking, ignored for --release builds",
           '?', False, type="choice", choices=["on", "off"], const="on", default="on")

add_option('disable-warnings-as-errors', "Don't add -Werror to compiler command line", 0, False)

add_option('propagate-shell-environment',
           "Pass shell environment to sub-processes (NEVER for production builds)",
           0, False)

add_option('variables-help',
           "Print the help text for SCons variables", 0, False)

add_option('cache',
           "Use an object cache rather than a per-build variant directory (experimental)",
           0, False)

add_option('cache-dir',
           "Specify the directory to use for caching objects if --cache is in use",
           1, False, default="$BUILD_ROOT/scons/cache")

try:
    with open("version.json", "r") as version_fp:
        version_data = json.load(version_fp)

    if 'version' not in version_data:
        print("version.json does not contain a version string")
        Exit(1)
    if 'githash' not in version_data:
        version_data['githash'] = utils.getGitVersion()

except IOError as e:
    # If the file error wasn't because the file is missing, error out
    if e.errno != errno.ENOENT:
        print("Error opening version.json: {0}".format(e.strerror))
        Exit(1)

    version_data = {
        'version': utils.getGitDescribe()[1:],
        'githash': utils.getGitVersion(),
    }

except ValueError as e:
    print("Error decoding version.json: {0}".format(e))
    Exit(1)


# Setup the command-line variables
def variable_shlex_converter(val):
    return shlex.split(val, posix=True)

def variable_distsrc_converter(val):
    if not val.endswith("/"):
        return val + "/"
    return val

env_vars = Variables()

env_vars.Add('ARFLAGS',
    help='Sets flags for the archiver',
    converter=variable_shlex_converter)

env_vars.Add('CCFLAGS',
    help='Sets flags for the C and C++ compiler',
    converter=variable_shlex_converter)

env_vars.Add('CFLAGS',
    help='Sets flags for the C compiler',
    converter=variable_shlex_converter)

env_vars.Add('CPPDEFINES',
    help='Sets pre-processor definitions for C and C++',
    converter=variable_shlex_converter)

env_vars.Add('CPPPATH',
    help='Adds paths to the preprocessor search path',
    converter=variable_shlex_converter)

env_vars.Add('CXXFLAGS',
    help='Sets flags for the C++ compiler',
    converter=variable_shlex_converter)

env_vars.Add('LIBPATH',
    help='Adds paths to the linker search path',
    converter=variable_shlex_converter)

env_vars.Add('LIBS',
    help='Adds extra libraries to link against',
    converter=variable_shlex_converter)

env_vars.Add('LINKFLAGS',
    help='Sets flags for the linker',
    converter=variable_shlex_converter)

env_vars.Add('MONGO_DIST_SRC_PREFIX',
    help='Sets the prefix for files in the source distribution archive',
    converter=variable_distsrc_converter,
    default="mongodb-src-r${MONGO_VERSION}")

env_vars.Add('MONGO_VERSION',
    help='Sets the version string for MongoDB',
    default=version_data['version'])

env_vars.Add('MONGO_GIT_HASH',
    help='Sets the githash to store in the MongoDB version information',
    default=version_data['githash'])

env_vars.Add('OBJCOPY',
    help='Sets the path to objcopy',
    default=WhereIs('objcopy'))

env_vars.Add('RPATH',
    help='Set the RPATH for dynamic libraries and executables',
    converter=variable_shlex_converter)

env_vars.Add('SHCCFLAGS',
    help='Sets flags for the C and C++ compiler when building shared libraries',
    converter=variable_shlex_converter)

env_vars.Add('SHCFLAGS',
    help='Sets flags for the C compiler when building shared libraries',
    converter=variable_shlex_converter)

env_vars.Add('SHCXXFLAGS',
    help='Sets flags for the C++ compiler when building shared libraries',
    converter=variable_shlex_converter)

env_vars.Add('SHLINKFLAGS',
    help='Sets flags for the linker when building shared libraries',
    converter=variable_shlex_converter)

env_vars.Add('STAGING_DIR',
    help='OpenWrt toolchain staging directory',
    default='$BUILD_ROOT')

# don't run configure if user calls --help
if GetOption('help'):
    Return()

# --- environment setup ---

# If the user isn't using the # to indicate top-of-tree or $ to expand a variable, forbid
# relative paths. Relative paths don't really work as expected, because they end up relative to
# the top level SConstruct, not the invokers CWD. We could in theory fix this with
# GetLaunchDir, but that seems a step too far.
buildDir = get_option('build-dir').rstrip('/')
if buildDir[0] not in ['$', '#']:
    if not os.path.isabs(buildDir):
        print("Do not use relative paths with --build-dir")
        Exit(1)

cacheDir = get_option('cache-dir').rstrip('/')
if cacheDir[0] not in ['$', '#']:
    if not os.path.isabs(cacheDir):
        print("Do not use relative paths with --cache-dir")
        Exit(1)

installDir = get_option('prefix').rstrip('/')
if installDir[0] not in ['$', '#']:
    if not os.path.isabs(installDir):
        print("Do not use relative paths with --prefix")
        Exit(1)

sconsDataDir = Dir(buildDir).Dir('scons')
SConsignFile(str(sconsDataDir.File('sconsign')))

def printLocalInfo():
    import sys, SCons
    print( "scons version: " + SCons.__version__ )
    print( "python version: " + " ".join( [ `i` for i in sys.version_info ] ) )

printLocalInfo()

boostLibs = [ "thread" , "filesystem" , "program_options", "system" ]

onlyServer = len( COMMAND_LINE_TARGETS ) == 0 or ( len( COMMAND_LINE_TARGETS ) == 1 and str( COMMAND_LINE_TARGETS[0] ) in [ "mongod" , "mongos" , "test" ] )

linux64  = False
force32 = has_option( "force32" ) 
force64 = has_option( "force64" )
if not force64 and not force32 and os.getcwd().endswith( "mongo-64" ):
    force64 = True
    print( "*** assuming you want a 64-bit build b/c of directory *** " )

releaseBuild = has_option("release")

if has_option("debugBuild") or has_option("debugBuildAndLogging"):
    print("Error: the --d and --dd flags are no longer permitted; use --dbg and --opt instead")
    Exit(1)

dbg_opt_mapping = {
    # --dbg, --opt   :   dbg    opt
    ( None,  None  ) : ( False, True ),
    ( None,  "on"  ) : ( False, True ),
    ( None,  "off" ) : ( False, False ),
    ( "on",  None  ) : ( True,  False ),  # special case interaction
    ( "on",  "on"  ) : ( True,  True ),
    ( "on",  "off" ) : ( True,  False ),
    ( "off", None  ) : ( False, True ),
    ( "off", "on"  ) : ( False, True ),
    ( "off", "off" ) : ( False, False ),
}
debugBuild, optBuild = dbg_opt_mapping[(get_option('dbg'), get_option('opt'))]

if releaseBuild and (debugBuild or not optBuild):
    print("Error: A --release build may not have debugging, and must have optimization")
    Exit(1)

static = has_option( "static" )

noshell = has_option( "noshell" ) 

jsEngine = get_option( "js-engine")

usev8 = (jsEngine != 'none')

v8version = jsEngine[3:] if jsEngine.startswith('v8-') else 'none'
v8suffix = '' if v8version == '3.12' else '-' + v8version

usePCH = has_option( "usePCH" )

tools = ['gcc', 'g++', 'gnulink', 'ar'] + [
    "gch", "jsheader", "mergelib", "mongo_unittest", "textfile", "distsrc", "gziptool"
]

staging_dir = '$BUILD_ROOT';
if has_option('staging-dir'):
    staging_dir = get_option('staging-dir')

# We defer building the env until we have determined whether we want certain values. Some values
# in the env actually have semantics for 'None' that differ from being absent, so it is better
# to build it up via a dict, and then construct the Environment in one shot with kwargs.
#
# Yes, BUILD_ROOT vs BUILD_DIR is confusing. Ideally, BUILD_DIR would actually be called
# VARIANT_DIR, and at some point we should probably do that renaming. Until we do though, we
# also need an Environment variable for the argument to --build-dir, which is the parent of all
# variant dirs. For now, we call that BUILD_ROOT. If and when we s/BUILD_DIR/VARIANT_DIR/g,
# then also s/BUILD_ROOT/BUILD_DIR/g.
envDict = dict(BUILD_ROOT=buildDir,
               BUILD_DIR=get_variant_dir(),
               DIST_ARCHIVE_SUFFIX='.tgz',
               EXTRAPATH=get_option("extrapath"),
               MODULE_BANNERS=[],
               ARCHIVE_ADDITION_DIR_MAP={},
               ARCHIVE_ADDITIONS=[],
               PYTHON=utils.find_python(),
               SERVER_ARCHIVE='${SERVER_DIST_BASENAME}${DIST_ARCHIVE_SUFFIX}',
               tools=tools,
               UNITTEST_ALIAS='unittests',
               # TODO: Move unittests.txt to $BUILD_DIR, but that requires
               # changes to MCI.
               UNITTEST_LIST='$BUILD_ROOT/unittests.txt',
               PYSYSPLATFORM=os.sys.platform,
               PCRE_VERSION='8.37',
               CONFIGUREDIR=sconsDataDir.Dir('sconf_temp'),
               CONFIGURELOG=sconsDataDir.File('config.log'),
               INSTALL_DIR=installDir,
               STAGING_DIR=staging_dir
               )

env = Environment(variables=env_vars, **envDict)
del envDict

env.Append( STAGING_DIR=staging_dir )

processor = "i386"

if has_option("distarch"):
    processor = get_option( "distarch")

if force32:
    if processor =="x86_64":
        processor = "i386"
    if processor =="aarch64":
        processor = "arm"
    if processor =="mips64":
        processor = "mips"
    if processor =="mipsel64":
        processor = "mipsel"
if force64:
    if processor =="i386":
        processor = "x86_64"
    if processor =="arm":
        processor = "aarch64"
    if processor =="mipsel":
        processor = "mipsel64"
    if processor =="mips":
        processor = "mips64"

env['PROCESSOR_ARCHITECTURE'] = processor

if has_option('variables-help'):
    print(env_vars.GenerateHelpText(env))
    Exit(0)

unknown_vars = env_vars.UnknownVariables()
if unknown_vars:
    print("Unknown variables specified: {0}".format(", ".join(unknown_vars.keys())))
    Exit(1)


# Add any scons options that conflict with scons variables here.
# The first item in each tuple is the option name and the second
# is the variable name
variable_conflicts = [
    ('libpath', 'LIBPATH'),
    ('cpppath', 'CPPPATH'),
    ('extrapath', 'CPPPATH'),
    ('extrapathdyn', 'CPPPATH'),
    ('extrapath', 'LIBPATH'),
    ('extrapathdyn', 'LIBPATH'),
    ('extralib', 'LIBS')
]

for (opt_name, var_name) in variable_conflicts:
    if has_option(opt_name) and var_name in env:
        print("Both option \"--{0}\" and variable {1} were specified".
            format(opt_name, var_name))
        Exit(1)

if has_option("cache"):
    EnsureSConsVersion( 2, 3, 0 )
    if has_option("release"):
        print("Using the experimental --cache option is not permitted for --release builds")
        Exit(1)
    if has_option("gcov"):
        print("Mixing --cache and --gcov doesn't work correctly yet. See SERVER-11084")
        Exit(1)
    env.CacheDir(str(env.Dir(cacheDir)))

if optBuild:
    env.Append( CPPDEFINES=["MONGO_OPTIMIZED_BUILD"] )

if has_option("propagate-shell-environment"):
    env['ENV'] = dict(os.environ);

# Ignore requests to build fast and loose for release builds.
# Also ignore fast-and-loose option if the scons cache is enabled (see SERVER-19088)
if get_option('build-fast-and-loose') == "on" and \
    not has_option('release') and not has_option('cache'):
    # See http://www.scons.org/wiki/GoFastButton for details
    env.Decider('MD5-timestamp')
    env.SetOption('max_drift', 1)

if has_option('mute'):
    env.Append( CCCOMSTR = "Compiling $TARGET" )
    env.Append( CXXCOMSTR = env["CCCOMSTR"] )
    env.Append( SHCCCOMSTR = "Compiling $TARGET" )
    env.Append( SHCXXCOMSTR = env["SHCCCOMSTR"] )
    env.Append( LINKCOMSTR = "Linking $TARGET" )
    env.Append( SHLINKCOMSTR = env["LINKCOMSTR"] )
    env.Append( ARCOMSTR = "Generating library $TARGET" )

endian = get_option( "endian" )

if endian == "auto":
    endian = sys.byteorder

if endian == "little":
    env.Append( CPPDEFINES=[("MONGO_BYTE_ORDER", "1234")] )
elif endian == "big":
    env.Append( CPPDEFINES=[("MONGO_BYTE_ORDER", "4321")] )

env['_LIBDEPS'] = '$_LIBDEPS_OBJS'

if env['_LIBDEPS'] == '$_LIBDEPS_OBJS':
    # The libraries we build in LIBDEPS_OBJS mode are just placeholders for tracking dependencies.
    # This avoids wasting time and disk IO on them.
    def write_uuid_to_file(env, target, source):
        with open(env.File(target[0]).abspath, 'w') as fake_lib:
            fake_lib.write(str(uuid.uuid4()))
            fake_lib.write('\n')

    def noop_action(env, target, source):
        pass

    env['ARCOM'] = write_uuid_to_file
    env['ARCOMSTR'] = 'Generating placeholder library $TARGET'
    env['RANLIBCOM'] = noop_action
    env['RANLIBCOMSTR'] = 'Skipping ranlib for $TARGET'

libdeps.setup_environment( env )

if env['PYSYSPLATFORM'] == 'linux3':
    env['PYSYSPLATFORM'] = 'linux2'

env['OS_FAMILY'] = 'posix'

env["ARCH"] = processor

if has_option( "cc-use-shell-environment" ) and has_option( "cc" ):
    print("Cannot specify both --cc-use-shell-environment and --cc")
    Exit(1)
elif has_option( "cxx-use-shell-environment" ) and has_option( "cxx" ):
    print("Cannot specify both --cxx-use-shell-environment and --cxx")
    Exit(1)

if has_option( "cxx-use-shell-environment" ):
    env["CXX"] = os.getenv("CXX");
    env["CC"] = env["CXX"]
if has_option( "cc-use-shell-environment" ):
    env["CC"] = os.getenv("CC");

if has_option( "cxx" ):
    if not has_option( "cc" ):
        print("Must specify C compiler when specifying C++ compiler")
        exit(1)
    env["CXX"] = get_option( "cxx" )
if has_option( "cc" ):
    if not has_option( "cxx" ):
        print("Must specify C++ compiler when specifying C compiler")
        exit(1)
    env["CC"] = get_option( "cc" )

if has_option( "ld" ):
    env["LINK"] = get_option( "ld" )

env['LINK_LIBGROUP_START'] = '-Wl,--start-group'
env['LINK_LIBGROUP_END'] = '-Wl,--end-group'
env['RELOBJ_LIBDEPS_START'] = '--whole-archive'
env['RELOBJ_LIBDEPS_END'] = '--no-whole-archive'
env['RELOBJ_LIBDEPS_ITEM'] = ''

if has_option( "libpath" ):
    env["LIBPATH"] = [get_option( "libpath" )]

if has_option( "cpppath" ):
    env["CPPPATH"] = [get_option( "cpppath" )]

env.Prepend( CPPDEFINES=[ "_SCONS" , 
                          "MONGO_EXPOSE_MACROS" ,
                          "PCRE_STATIC",  # for pcre on Windows
                          "SUPPORT_UTF8" ],  # for pcre
)

if has_option( "safeshell" ):
    env.Append( CPPDEFINES=[ "MONGO_SAFE_SHELL" ] )

if has_option( "durableDefaultOn" ):
    env.Append( CPPDEFINES=[ "_DURABLEDEFAULTON" ] )

if has_option( "durableDefaultOff" ):
    env.Append( CPPDEFINES=[ "_DURABLEDEFAULTOFF" ] )

extraLibPlaces = []

env['EXTRACPPPATH'] = []
env['EXTRALIBPATH'] = []
env['EXTRABINPATH'] = []

def addExtraLibs( s ):
    for x in s.split(","):
        env.Append( EXTRABINPATH=[ x + "/bin" ] )
        env.Append( EXTRACPPPATH=[ x + "/include" ] )
        env.Append( EXTRALIBPATH=[ x + "/lib" ] )
        env.Append( EXTRALIBPATH=[ x + "/lib64" ] )
        extraLibPlaces.append( x + "/lib" )

if has_option( "extrapath" ):
    addExtraLibs( GetOption( "extrapath" ) )

if has_option( "extrapathdyn" ):
    addExtraLibs( GetOption( "extrapathdyn" ) )

if has_option( "extralib" ):
    for x in GetOption( "extralib" ).split( "," ):
        env.Append( LIBS=[ x ] )

# ---- other build setup -----

nixLibPrefix = "lib"

dontReplacePackage = False
isBuildingLatest = False

def filterExists(paths):
    return filter(os.path.exists, paths)

env.Append( LIBS=['m'] )

if os.uname()[4] == "x86_64" and not force32:
    linux64 = True
    nixLibPrefix = "lib64"
    env.Append( EXTRALIBPATH=["/usr/lib64" , "/lib64" ] )
    env.Append( LIBS=["pthread"] )

    force64 = False

if force32:
    env.Append( EXTRALIBPATH=["/usr/lib32"] )

if static:
    env.Append( LINKFLAGS=" -static " )

env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1

if has_option( "static-libstdc++" ):
    env.Append( LINKFLAGS=["-static-libstdc++", "-static-libgcc"] )

if has_option( "distcc" ):
    env["CXX"] = "distcc " + env["CXX"]

# -Winvalid-pch Warn if a precompiled header (see Precompiled Headers) is found in the search path but can't be used.
env.Append( CCFLAGS=["-fno-omit-frame-pointer",
                        "-fPIC",
                        "-fno-strict-aliasing",
                        "-ggdb",
                        "-pthread",
                        "-Wall",
                        "-Wsign-compare",
                        "-Wno-unknown-pragmas",
                        "-Winvalid-pch"] )
# env.Append( " -Wconversion" ) TODO: this doesn't really work yet
env.Append( CCFLAGS=["-pipe"] )
if not has_option("disable-warnings-as-errors"):
    env.Append( CCFLAGS=["-Werror"] )

env.Append( CPPDEFINES=["_FILE_OFFSET_BITS=64"] )
env.Append( CXXFLAGS=["-Wnon-virtual-dtor", "-Woverloaded-virtual"] )
env.Append( LINKFLAGS=["-fPIC", "-pthread"] )

# SERVER-9761: Ensure early detection of missing symbols in dependent libraries at program
# startup.
#
# TODO: Is it necessary to add to both linkflags and shlinkflags, or are LINKFLAGS
# propagated to SHLINKFLAGS?
env.Append( LINKFLAGS=["-Wl,-z,now"] )
env.Append( SHLINKFLAGS=["-Wl,-z,now"] )

env.Append( LINKFLAGS=["-rdynamic"] )

env.Append( LIBS=[] )

#make scons colorgcc friendly
for key in ('HOME', 'TERM'):
    try:
        env['ENV'][key] = os.environ[key]
    except KeyError:
        pass

if has_option( "gcov" ):
    env.Append( CXXFLAGS=" -fprofile-arcs -ftest-coverage " )
    env.Append( CPPDEFINES=["MONGO_GCOV"] )
    env.Append( LINKFLAGS=" -fprofile-arcs -ftest-coverage " )

if optBuild:
    env.Append( CCFLAGS=["-O3"] )
else:
    env.Append( CCFLAGS=["-O0"] )

if debugBuild:
    if not optBuild:
        env.Append( CCFLAGS=["-fstack-protector"] )
        env.Append( LINKFLAGS=["-fstack-protector"] )
        env.Append( SHLINKFLAGS=["-fstack-protector"] )
    env['ENV']['GLIBCXX_FORCE_NEW'] = 1; # play nice with valgrind
    env.Append( CPPDEFINES=["_DEBUG"] );

if force64:
    env.Append( CCFLAGS="-m64" )
    env.Append( LINKFLAGS="-m64" )

if force32:
    env.Append( CCFLAGS="-m32" )
    env.Append( LINKFLAGS="-m32" )

if has_option( "gdbserver" ):
    env.Append( CPPDEFINES=["USE_GDBSERVER"] )

if "uname" in dir(os):
    hacks = buildscripts.findHacks( os.uname() )
    if hacks is not None:
        hacks.insert( env , { "linux64" : linux64 } )

wiredtiger = (get_option('wiredtiger') == 'on')

try:
    umask = os.umask(022)
except OSError:
    pass

for keysuffix in [ "1" , "2" ]:
    keyfile = "jstests/libs/key%s" % keysuffix
    os.chmod( keyfile , stat.S_IWUSR|stat.S_IRUSR )

# boostSuffixList is used when using system boost to select a search sequence
# for boost libraries.
boostSuffixList = ["-mt", ""]
if get_option("system-boost-lib-search-suffixes") is not None:
    boostSuffixList = get_option("system-boost-lib-search-suffixes")
    if boostSuffixList == "":
        boostSuffixList = []
    else:
        boostSuffixList = boostSuffixList.split(',')

env.Append( CPPPATH=['$EXTRACPPPATH'],
            LIBPATH=['$EXTRALIBPATH'] )

# discover modules, and load the (python) module for each module's build.py
mongo_modules = moduleconfig.discover_modules('src/mongo/db/modules')
env['MONGO_MODULES'] = [m.name for m in mongo_modules]

# --- check system ---

def doConfigure(myenv):
    global wiredtiger

    # Check that the compilers work.
    #
    # TODO: Currently, we have some flags already injected. Eventually, this should test the
    # bare compilers, and we should re-check at the very end that TryCompile and TryLink still
    # work with the flags we have selected.
    conf = Configure(myenv, help=False)

    if 'CheckCXX' in dir( conf ):
        if not conf.CheckCXX():
            print("C++ compiler %s does not work" % (conf.env["CXX"]))
            Exit(1)

    # Only do C checks if CC != CXX
    check_c = (myenv["CC"] != myenv["CXX"])

    if check_c and 'CheckCC' in dir( conf ):
        if not conf.CheckCC():
            print("C compiler %s does not work" % (conf.env["CC"]))
            Exit(1)
    myenv = conf.Finish()

    # Identify the toolchain in use. We currently support the following:
    # TODO: Goes in the env?

    def CheckForToolchain(context, toolchain, lang_name, compiler_var, source_suffix):
        test_bodies = {
            "GCC" : (
                # Clang also defines __GNUC__
                """
                #if !defined(__GNUC__) || defined(__clang__)
                #error
                #endif
                """),
        }
        print_tuple = (lang_name, context.env[compiler_var], toolchain)
        context.Message('Checking if %s compiler "%s" is %s... ' % print_tuple)
        # Strip indentation from the test body to ensure that the newline at the end of the
        # endif is the last character in the file (rather than a line of spaces with no
        # newline), and that all of the preprocessor directives start at column zero. Both of
        # these issues can trip up older toolchains.
        test_body = textwrap.dedent(test_bodies[toolchain])
        result = context.TryCompile(test_body, source_suffix)
        context.Result(result)
        return result

    conf = Configure(myenv, help=False, custom_tests = {
        'CheckForToolchain' : CheckForToolchain,
    })

    if not conf.CheckForToolchain("GCC", "C++", "CXX", ".cpp"):
        print("GCC toolchain not found")
        Exit(1)

    myenv = conf.Finish()

    compiler_minimum_string = "GCC 4.8.2"
    compiler_test_body = textwrap.dedent(
    """
    #if !defined(__GNUC__) || defined(__clang__)
    #error
    #endif

    #if (__GNUC__ < 4) || (__GNUC__ == 4 && __GNUC_MINOR__ < 8) || (__GNUC__ == 4 && __GNUC_MINOR__ == 8 && __GNUC_PATCHLEVEL__ < 2)
    #error %s or newer is required to build MongoDB
    #endif

    int main(int argc, char* argv[]) {
        return 0;
    }
    """ % compiler_minimum_string)

    def CheckForMinimumCompiler(context, language):
        extension_for = {
            "C" : ".c",
            "C++" : ".cpp",
        }
        context.Message("Checking if %s compiler is %s or newer..." %
                        (language, compiler_minimum_string))
        result = context.TryCompile(compiler_test_body, extension_for[language])
        context.Result(result)
        return result;

    conf = Configure(myenv, help=False, custom_tests = {
        'CheckForMinimumCompiler' : CheckForMinimumCompiler,
    })

    c_compiler_validated = True
    if check_c:
        c_compiler_validated = conf.CheckForMinimumCompiler('C')
    cxx_compiler_validated = conf.CheckForMinimumCompiler('C++')

    myenv = conf.Finish();

    suppress_invalid = has_option("disable-minimum-compiler-version-enforcement")
    if releaseBuild and suppress_invalid:
        print("--disable-minimum-compiler-version-enforcement is forbidden with --release")
        Exit(1)

    if not (c_compiler_validated and cxx_compiler_validated):
        if not suppress_invalid:
            print("ERROR: Refusing to build with compiler that does not meet requirements")
            Exit(1)
        print("WARNING: Ignoring failed compiler version check per explicit user request.")
        print("WARNING: The build may fail, binaries may crash, or may run but corrupt data...")

    def CheckForx86(context):
        # See http://nadeausoftware.com/articles/2012/02/c_c_tip_how_detect_processor_type_using_compiler_predefined_macros
        test_body = """
        #if defined(__i386) || defined(_M_IX86)
        /* x86 32-bit */
        #else
        #error not 32-bit x86
        #endif
        """
        context.Message('Checking if target architecture is 32-bit x86...')
        ret = context.TryCompile(textwrap.dedent(test_body), ".c")
        context.Result(ret)
        return ret

    conf = Configure(myenv, help=False, custom_tests = {
        'CheckForx86' : CheckForx86,
    })

    if conf.CheckForx86():

        # If we are using GCC or clang to target 32 or x86, set the ISA minimum to 'nocona',
        # and the tuning to 'generic'. The choice of 'nocona' is selected because it
        #  -- includes MMX extenions which we need for tcmalloc on 32-bit
        #  -- can target 32 bit
        #  -- is at the time of this writing a widely-deployed 10 year old microarchitecture
        #  -- is available as a target architecture from GCC 4.0+
        # However, we only want to select an ISA, not the nocona specific scheduling, so we
        # select the generic tuning. For installations where hardware and system compiler rev are
        # contemporaries, the generic scheduling should be appropriate for a wide range of
        # deployed hardware.

        myenv.Append( CCFLAGS=['-march=nocona', '-mtune=generic'] )

        # Wiredtiger only supports 64-bit architecture, and will fail to compile on 32-bit
        # so disable WiredTiger automatically on 32-bit since wiredtiger is on by default
        if wiredtiger == True:
            print("WARNING: WiredTiger is not supported on 32-bit platforms, disabling support")
            wiredtiger = False
    conf.Finish()

    # Enable PCH if we are on using gcc or clang and the 'Gch' tool is enabled. Otherwise,
    # remove any pre-compiled header since the compiler may try to use it if it exists.
    if usePCH:
        if 'Gch' in dir( myenv ):
            myenv['Gch'] = myenv.Gch( "$BUILD_DIR/mongo/pch.h$GCHSUFFIX",
                                        "src/mongo/pch.h" )[0]
            myenv['GchSh'] = myenv[ 'Gch' ]
    elif os.path.exists( myenv.File("$BUILD_DIR/mongo/pch.h$GCHSUFFIX").abspath ):
        print( "removing precompiled headers" )
        os.unlink( myenv.File("$BUILD_DIR/mongo/pch.h.$GCHSUFFIX").abspath )

    def AddFlagIfSupported(env, tool, extension, flag, **mutation):
        def CheckFlagTest(context, tool, extension, flag):
            test_body = ""
            context.Message('Checking if %s compiler supports %s... ' % (tool, flag))
            ret = context.TryCompile(test_body, extension)
            context.Result(ret)
            return ret

        test_mutation = mutation
        
        test_mutation = copy.deepcopy(mutation)
        # GCC helpfully doesn't issue a diagnostic on unknown flags of the form -Wno-xxx
        # unless other diagnostics are triggered. That makes it tough to check for support
        # for -Wno-xxx. To work around, if we see that we are testing for a flag of the
        # form -Wno-xxx (but not -Wno-error=xxx), we also add -Wxxx to the flags. GCC does
        # warn on unknown -Wxxx style flags, so this lets us probe for availablity of
        # -Wno-xxx.
        for kw in test_mutation.keys():
            test_flags = test_mutation[kw]
            for test_flag in test_flags:
                if test_flag.startswith("-Wno-") and not test_flag.startswith("-Wno-error="):
                    test_flags.append(re.sub("^-Wno-", "-W", test_flag))

        cloned = env.Clone()
        cloned.Append(**test_mutation)

        # For GCC, we don't need anything since bad flags are already errors, but
        # adding -Werror won't hurt. For clang, bad flags are only warnings, so we need -Werror
        # to make them real errors.
        cloned.Append(CCFLAGS=['-Werror'])
        conf = Configure(cloned, help=False, custom_tests = {
                'CheckFlag' : lambda(ctx) : CheckFlagTest(ctx, tool, extension, flag)
        })
        available = conf.CheckFlag()
        conf.Finish()
        if available:
            env.Append(**mutation)
        return available

    def AddToCFLAGSIfSupported(env, flag):
        return AddFlagIfSupported(env, 'C', '.c', flag, CFLAGS=[flag])

    def AddToCCFLAGSIfSupported(env, flag):
        return AddFlagIfSupported(env, 'C', '.c', flag, CCFLAGS=[flag])

    def AddToCXXFLAGSIfSupported(env, flag):
        return AddFlagIfSupported(env, 'C++', '.cpp', flag, CXXFLAGS=[flag])

    # This warning was added in g++-4.8.
    AddToCCFLAGSIfSupported(myenv, '-Wno-unused-local-typedefs')

    # Clang likes to warn about unused functions, which seems a tad aggressive and breaks
    # -Werror, which we want to be able to use.
    AddToCCFLAGSIfSupported(myenv, '-Wno-unused-function')

    # TODO: Note that the following two flags are added to CCFLAGS even though they are
    # really C++ specific. We need to do this because SCons passes CXXFLAGS *before*
    # CCFLAGS, but CCFLAGS contains -Wall, which re-enables the warnings we are trying to
    # suppress. In the future, we should move all warning flags to CCWARNFLAGS and
    # CXXWARNFLAGS and add these to CCOM and CXXCOM as appropriate.
    #
    # Clang likes to warn about unused private fields, but some of our third_party
    # libraries have such things.
    AddToCCFLAGSIfSupported(myenv, '-Wno-unused-private-field')

    # Prevents warning about using deprecated features (such as auto_ptr in c++11)
    # Using -Wno-error=deprecated-declarations does not seem to work on some compilers,
    # including at least g++-4.6.
    AddToCCFLAGSIfSupported(myenv, "-Wno-deprecated-declarations")

    # As of clang-3.4, this warning appears in v8, and gets escalated to an error.
    AddToCCFLAGSIfSupported(myenv, "-Wno-tautological-constant-out-of-range-compare")

    # New in clang-3.4, trips up things mostly in third_party, but in a few places in the
    # primary mongo sources as well.
    AddToCCFLAGSIfSupported(myenv, "-Wno-unused-const-variable")

    # Prevents warning about unused but set variables found in boost version 1.49
    # in boost/date_time/format_date_parser.hpp which does not work for compilers
    # GCC >= 4.6. Error explained in https://svn.boost.org/trac/boost/ticket/6136 .
    AddToCCFLAGSIfSupported(myenv, "-Wno-unused-but-set-variable")

    # This has been suppressed in gcc 4.8, due to false positives, but not in clang.  So
    # we explicitly disable it here.
    AddToCCFLAGSIfSupported(myenv, "-Wno-missing-braces")

    # Suppress warnings about not consistently using override everywhere in a class. It seems
    # very pedantic, and we have a fair number of instances.
    AddToCCFLAGSIfSupported(myenv, "-Wno-inconsistent-missing-override")

    # Don't issue warnings about potentially evaluated expressions
    AddToCCFLAGSIfSupported(myenv, "-Wno-potentially-evaluated-expression")

    usingLibStdCxx = False
    if has_option('libc++'):
        print( 'libc++ is currently only supported for clang')
        Exit(1)
    else:
        def CheckLibStdCxx(context):
            test_body = """
            #include <vector>
            #if !defined(__GLIBCXX__)
            #error
            #endif
            """

            context.Message('Checking if we are using libstdc++... ')
            ret = context.TryCompile(textwrap.dedent(test_body), ".cpp")
            context.Result(ret)
            return ret

        conf = Configure(myenv, help=False, custom_tests = {
            'CheckLibStdCxx' : CheckLibStdCxx,
        })
        usingLibStdCxx = conf.CheckLibStdCxx()
        conf.Finish()

    # Check to see if we are trying to use an elderly libstdc++, which we arbitrarily define as
    # 4.6.0. This is primarly to help people using clang in C++11 mode on OS X but forgetting
    # to use --libc++. We also use it to decide if we trust the libstdc++ debug mode. We would,
    # ideally, check the __GLIBCXX__ version, but for various reasons this is not
    # workable. Instead, we switch on the fact that _GLIBCXX_BEGIN_NAMESPACE_VERSION wasn't
    # introduced until libstdc++ 4.6.0.

    haveGoodLibStdCxx = False
    if usingLibStdCxx:

        def CheckModernLibStdCxx(context):

            test_body = """
            #include <vector>
            #if !defined(_GLIBCXX_BEGIN_NAMESPACE_VERSION)
            #error libstdcxx older than 4.6.0
            #endif
            """

            context.Message('Checking for libstdc++ 4.6.0 or better... ')
            ret = context.TryCompile(textwrap.dedent(test_body), ".cpp")
            context.Result(ret)
            return ret

        conf = Configure(myenv, help=False, custom_tests = {
            'CheckModernLibStdCxx' : CheckModernLibStdCxx,
        })
        haveGoodLibStdCxx = conf.CheckModernLibStdCxx()
        conf.Finish()

    # Sort out whether we can and should use C++11:
    cxx11_mode = get_option("c++11")

    # If we are using libstdc++, only allow C++11 mode with our line-in-the-sand good
    # libstdc++. As always, if in auto mode fall back to disabling if we don't have a good
    # libstdc++, otherwise fail the build because we can't honor the explicit request.
    if cxx11_mode != "off" and usingLibStdCxx:
        if not haveGoodLibStdCxx:
            if cxx11_mode == "auto":
                cxx11_mode = "off"
            else:
                print( 'Detected libstdc++ is too old to support C++11 mode' )
                Exit(1)

    # We are going to be adding flags to the environment, but we don't want to persist
    # those changes unless we pass all the below checks. Make a copy of the environment
    # that we will modify, we will only "commit" the changes to the env if we pass all the
    # checks.
    cxx11Env = myenv.Clone()

    # For our other compilers (gcc and clang) we need to pass -std=c++0x or -std=c++11,
    # but we prefer the latter. Try that first, and fall back to c++0x if we don't
    # detect that --std=c++11 works. If we can't find a flag and C++11 was explicitly
    # requested, error out, otherwise turn off C++11 support in auto mode.
    if cxx11_mode != "off":
        if not AddToCXXFLAGSIfSupported(cxx11Env, '-std=c++11'):
            if not AddToCXXFLAGSIfSupported(cxx11Env, '-std=c++0x'):
                if cxx11_mode == "auto":
                    cxx11_mode = "off"
                else:
                    print( 'C++11 compiler support is required, but cannot find a flag to enable it' )
                    Exit(1)

    # We appear to have C++11, or at least a flag to enable it, which is now set in the
    # environment. If we are in auto mode, check if the compiler claims that it strictly
    # supports C++11, and disable C++11 if not. If the user has explicitly requested C++11,
    # we don't care about what the compiler claims to support, trust the user.
    if cxx11_mode == "auto":
        def CheckCxx11Official(context):
            test_body = """
            #if __cplusplus < 201103L
            #error
            #endif
            const int not_an_empty_file = 0;
            """

            context.Message('Checking if __cplusplus >= 201103L to auto-enable C++11... ')
            ret = context.TryCompile(textwrap.dedent(test_body), ".cpp")
            context.Result(ret)
            return ret

        conf = Configure(cxx11Env, help=False, custom_tests = {
            'CheckCxx11Official' : CheckCxx11Official,
        })

        if cxx11_mode == "auto" and not conf.CheckCxx11Official():
            cxx11_mode = "off"

        conf.Finish()

    # We require c99 mode for C files when C++11 is enabled, so perform the same dance
    # as above: if C++11 mode is not off, try the flag, if we are in auto mode and we fail
    # then turn off C++11, otherwise C++11 was explicitly requested and we should error out.
    if cxx11_mode != "off":
        if not AddToCFLAGSIfSupported(cxx11Env, '-std=c99'):
            if cxx11_mode == "auto":
                cxx11_mode = "off"
            else:
                print( "C99 compiler support is required, but compiler doesn't honor -std=c99" )
                Exit(1)

    # If we got here and cxx11_mode hasn't become false, then its true, so swap in the
    # modified environment.
    if cxx11_mode != "off":
        cxx11_mode = "on"
        myenv = cxx11Env

    # rocksdb requires C++11 mode
    if has_option("rocksdb") and cxx11_mode == "off":
        print("--rocksdb requires C++11 mode to be enabled");
        Exit(1)

    if has_option("use-glibcxx-debug"):
        # If we are using a modern libstdc++ and this is a debug build and we control all C++
        # dependencies, then turn on the debugging features in libstdc++.
        if not debugBuild:
            print("--use-glibcxx-debug requires --dbg=on")
            Exit(1)
        if not usingLibStdCxx or not haveGoodLibStdCxx:
            print("--use-glibcxx-debug is only compatible with the GNU implementation of the "
                  "C++ standard libary, and requires minimum version 4.6")
            Exit(1)
        myenv.Append(CPPDEFINES=["_GLIBCXX_DEBUG"]);

    if has_option('sanitize'):

        if not (using_clang() or using_gcc()):
            print( 'sanitize is only supported with clang or gcc')
            Exit(1)

        sanitizer_list = get_option('sanitize').split(',')

        using_lsan = 'leak' in sanitizer_list
        using_asan = 'address' in sanitizer_list or using_lsan

        if using_asan:
            if get_option('allocator') == 'tcmalloc':
                print("Cannot use address or leak sanitizer with tcmalloc")
                Exit(1)

        # If the user asked for leak sanitizer turn on the detect_leaks
        # ASAN_OPTION. If they asked for address sanitizer as well, drop
        # 'leak', because -fsanitize=leak means no address.
        #
        # --sanitize=leak:           -fsanitize=leak, detect_leaks=1
        # --sanitize=address,leak:   -fsanitize=address, detect_leaks=1
        # --sanitize=address:        -fsanitize=address
        #
        if using_lsan:
            if using_asan:
                myenv['ENV']['ASAN_OPTIONS'] = "detect_leaks=1"
            myenv['ENV']['LSAN_OPTIONS'] = "suppressions=%s" % myenv.File("#etc/lsan.suppressions").abspath
            if 'address' in sanitizer_list:
                sanitizer_list.remove('leak')

        sanitizer_option = '-fsanitize=' + ','.join(sanitizer_list)

        if AddToCCFLAGSIfSupported(myenv, sanitizer_option):
            myenv.Append(LINKFLAGS=[sanitizer_option])
            myenv.Append(CCFLAGS=['-fno-omit-frame-pointer'])
        else:
            print( 'Failed to enable sanitizers with flag: ' + sanitizer_option )
            Exit(1)

        blackfiles_map = {
            "address" : myenv.File("#etc/asan.blacklist"),
            "leak" : myenv.File("#etc/asan.blacklist"),
            "thread" : myenv.File("#etc/tsan.blacklist"),
            "undefined" : myenv.File("#etc/ubsan.blacklist"),
        }

        blackfiles = set([v for (k, v) in blackfiles_map.iteritems() if k in sanitizer_list])
        blacklist_options=["-fsanitize-blacklist=%s" % blackfile for blackfile in blackfiles]

        for blacklist_option in blacklist_options:
            if AddToCCFLAGSIfSupported(myenv, blacklist_option):
                myenv.Append(LINKFLAGS=[blacklist_option])

        llvm_symbolizer = get_option('llvm-symbolizer')
        if os.path.isabs(llvm_symbolizer):
            if not myenv.File(llvm_symbolizer).exists():
                print("WARNING: Specified symbolizer '%s' not found" % llvm_symbolizer)
                llvm_symbolizer = None
        else:
            llvm_symbolizer = myenv.WhereIs(llvm_symbolizer)

        if llvm_symbolizer:
            myenv['ENV']['ASAN_SYMBOLIZER_PATH'] = llvm_symbolizer
            myenv['ENV']['LSAN_SYMBOLIZER_PATH'] = llvm_symbolizer
        elif using_lsan:
            print("Using the leak sanitizer requires a valid symbolizer")
            Exit(1)

    # Apply any link time optimization settings as selected by the 'lto' option.
    if has_option('lto'):
        # For GCC and clang, the flag is -flto, and we need to pass it both on the compile
        # and link lines.
        if AddToCCFLAGSIfSupported(myenv, '-flto'):
            myenv.Append(LINKFLAGS=['-flto'])

            def LinkHelloWorld(context, adornment = None):
                test_body = """
                #include <iostream>
                int main() {
                    std::cout << "Hello, World!" << std::endl;
                    return 0;
                }
                """
                message = "Trying to link with LTO"
                if adornment:
                    message = message + " " + adornment
                message = message + "..."
                context.Message(message)
                ret = context.TryLink(textwrap.dedent(test_body), ".cpp")
                context.Result(ret)
                return ret

            conf = Configure(myenv, help=False, custom_tests = {
                'LinkHelloWorld' : LinkHelloWorld,
            })

            # Some systems (clang, on a system with the BFD linker by default) may need to
            # explicitly request the gold linker for LTO to work. If we can't LTO link a
            # simple program, see if -fuse=ld=gold helps.
            if not conf.LinkHelloWorld():
                conf.env.Append(LINKFLAGS=["-fuse-ld=gold"])
                if not conf.LinkHelloWorld("(with -fuse-ld=gold)"):
                    print("Error: Couldn't link with LTO")
                    Exit(1)

            myenv = conf.Finish()

        else:
            print( "Link time optimization requested, " +
                    "but selected compiler does not honor -flto" )
            Exit(1)

    # glibc's memcmp is faster than gcc's
    AddToCCFLAGSIfSupported(myenv, "-fno-builtin-memcmp")

    # When using msvc, check for support for __declspec(thread), unless we have been asked
    # explicitly not to use it. For other compilers, see if __thread works.
    def CheckUUThread(context):
        test_body = """
        __thread int tsp_int;
        int main(int argc, char* argv[]) {
            tsp_int = argc;
            return 0;
        }
        """
        context.Message('Checking for __thread... ')
        ret = context.TryLink(textwrap.dedent(test_body), ".cpp")
        context.Result(ret)
        return ret
    conf = Configure(myenv, help=False, custom_tests = {
        'CheckUUThread' : CheckUUThread,
    })
    haveUUThread = conf.CheckUUThread()
    conf.Finish()
    if haveUUThread:
        myenv.Append(CPPDEFINES=['MONGO_HAVE___THREAD'])

    def CheckCXX11Atomics(context):
        test_body = """
        #include <atomic>
        int main(int argc, char **argv) {
            std::atomic<int> a(0);
            return a.fetch_add(1);
        }
        """
        context.Message('Checking for C++11 <atomic> support... ')
        ret = context.TryLink(textwrap.dedent(test_body), '.cpp')
        context.Result(ret)
        return ret;

    def CheckGCCAtomicBuiltins(context):
        test_body = """
        int main(int argc, char **argv) {
            int a = 0;
            int b = 0;
            int c = 0;

            __atomic_compare_exchange(&a, &b, &c, false, __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST);
            return 0;
        }
        """
        context.Message('Checking for gcc __atomic builtins... ')
        ret = context.TryLink(textwrap.dedent(test_body), '.cpp')
        context.Result(ret)
        return ret

    def CheckGCCSyncBuiltins(context):
        test_body = """
        int main(int argc, char **argv) {
            int a = 0;
            return __sync_fetch_and_add(&a, 1);
        }

        //
        // Figure out if we are using gcc older than 4.2 to target 32-bit x86. If so, error out
        // even if we were able to compile the __sync statement, due to
        // https://gcc.gnu.org/bugzilla/show_bug.cgi?id=40693
        //
        #if defined(__i386__)
        #if !defined(__clang__)
        #if defined(__GNUC__) && (__GNUC__ == 4) && (__GNUC_MINOR__ < 2)
        #error "Refusing to use __sync in 32-bit mode with gcc older than 4.2"
        #endif
        #endif
        #endif
        """

        context.Message('Checking for useable __sync builtins... ')
        ret = context.TryLink(textwrap.dedent(test_body), '.cpp')
        context.Result(ret)
        return ret

    # not all C++11-enabled gcc versions have type properties
    def CheckCXX11IsTriviallyCopyable(context):
        test_body = """
        #include <type_traits>
        int main(int argc, char **argv) {
            class Trivial {
                int trivial1;
                double trivial2;
                struct {
                    float trivial3;
                    short trivial4;
                } trivial_member;
            };

            class NotTrivial {
                int x, y;
                NotTrivial(const NotTrivial& o) : x(o.y), y(o.x) {}
            };

            static_assert(std::is_trivially_copyable<Trivial>::value,
                          "I should be trivially copyable");
            static_assert(!std::is_trivially_copyable<NotTrivial>::value,
                          "I should not be trivially copyable");
            return 0;
        }
        """
        context.Message('Checking for C++11 is_trivially_copyable support... ')
        ret = context.TryCompile(textwrap.dedent(test_body), '.cpp')
        context.Result(ret)
        return ret

    conf = Configure(myenv, help=False, custom_tests = {
        'CheckCXX11Atomics': CheckCXX11Atomics,
        'CheckGCCAtomicBuiltins': CheckGCCAtomicBuiltins,
        'CheckGCCSyncBuiltins': CheckGCCSyncBuiltins,
        'CheckCXX11IsTriviallyCopyable': CheckCXX11IsTriviallyCopyable,
    })

    # Figure out what atomics mode to use by way of the tests defined above.
    #
    # Windows: <atomic> > Interlocked functions / intrinsics.
    #
    # If we are in C++11 mode, try to use <atomic>. This is unusual for us, as typically we
    # only use __cplusplus >= 201103L to decide if we want to enable a feature. We make a
    # special case for the atomics and use them on platforms that offer them even if they don't
    # advertise full conformance. For MSVC systems, if we don't have <atomic> then no more
    # checks are required. Otherwise, we are on a GCC/clang system, where we may have __atomic
    # or __sync, so try those in that order next.
    #
    # If we don't end up defining a MONGO_HAVE for the atomics, we will end up falling back to
    # the Microsoft Interlocked functions/intrinsics when using MSVC, or the gcc_intel
    # implementation of hand-rolled assembly if using gcc/clang.

    # Prefer the __atomic builtins. If we don't have those, try for __sync. Otherwise
    # atomic_intrinsics.h will try to fall back to the hand-rolled assembly implementations
    # in atomic_intrinsics_gcc_intel for x86 platforms.
    if conf.CheckGCCAtomicBuiltins():
        conf.env.Append(CPPDEFINES=["MONGO_HAVE_GCC_ATOMIC_BUILTINS"])
    else:
        if conf.CheckGCCSyncBuiltins():
            conf.env.Append(CPPDEFINES=["MONGO_HAVE_GCC_SYNC_BUILTINS"])

    if (cxx11_mode == "on") and conf.CheckCXX11IsTriviallyCopyable():
        conf.env.Append(CPPDEFINES=['MONGO_HAVE_STD_IS_TRIVIALLY_COPYABLE'])

    myenv = conf.Finish()

    conf = Configure(myenv)
    libdeps.setup_conftests(conf)

    def checkOpenSSL(conf):
        sslLibName = "ssl"
        cryptoLibName = "crypto"

        if not conf.CheckLibWithHeader(
                cryptoLibName,
                ["openssl/crypto.h"],
                "C",
                "SSLeay_version(0);",
                autoadd=True):
            conf.env.ConfError("Couldn't find OpenSSL crypto.h header and library")

        if not conf.CheckLibWithHeader(
                sslLibName,
                ["openssl/ssl.h"],
                "C",
                "SSL_version(NULL);",
                autoadd=True):
            conf.env.ConfError("Couldn't find OpenSSL ssl.h header and library")

        def CheckLinkSSL(context):
            test_body = """
            #include <openssl/err.h>
            #include <openssl/ssl.h>
            #include <stdlib.h>

            int main() {
                SSL_library_init();
                SSL_load_error_strings();
                ERR_load_crypto_strings();

                OpenSSL_add_all_algorithms();
                ERR_free_strings();

                return EXIT_SUCCESS;
            }
            """
            context.Message("Checking that linking to OpenSSL works...")
            ret = context.TryLink(textwrap.dedent(test_body), ".c")
            context.Result(ret)
            return ret

        conf.AddTest("CheckLinkSSL", CheckLinkSSL)

        if not conf.CheckLinkSSL():
            conf.env.ConfError("SSL is enabled, but is unavailable")

        if conf.CheckDeclaration(
            "FIPS_mode_set",
            includes="""
                #include <openssl/crypto.h>
                #include <openssl/evp.h>
            """):
            conf.env.Append(CPPDEFINES=["MONGO_HAVE_FIPS_MODE_SET"])

    if has_option("ssl"):
        checkOpenSSL(conf)

        conf.env.Append(
            MONGO_CRYPTO=["openssl"],
            CPPDEFINES=["MONGO_SSL"]
        )
    else:
        # If we don't need an SSL build, we can get by with TomCrypt.
        conf.env.Append( MONGO_CRYPTO=["tom"] )

    conf.FindSysLibDep("stemmer", ["stemmer"])

    conf.FindSysLibDep("snappy", ["snappy"])

    conf.FindSysLibDep("s2", ["s2"])

    conf.CheckLib('pcre')
    conf.CheckLib('pcrecpp')

    conf.FindSysLibDep("pcre", ["pcre"])
    conf.FindSysLibDep("pcrecpp", ["pcrecpp"])

    conf.FindSysLibDep("zlib", ["z"])

    conf.FindSysLibDep("yaml", ["yaml-cpp"])

    conf.FindSysLibDep("tcmalloc", ["tcmalloc_minimal"])

    conf.env.Append(
        CPPDEFINES=[
            "BOOST_SYSTEM_NO_DEPRECATED",
        ]
    )

    if not conf.CheckCXXHeader( "boost/filesystem/operations.hpp" ):
        print( "can't find boost headers" )
        Exit(1)

    conf.env.Append(CPPDEFINES=[("BOOST_THREAD_VERSION", "2")])

    # Note that on Windows with using-system-boost builds, the following
    # FindSysLibDep calls do nothing useful (but nothing problematic either)
    #
    # NOTE: Pass --system-boost-lib-search-suffixes= to suppress these checks, which you
    # might want to do if using autolib linking on Windows, for example.
    if boostSuffixList:
        for b in boostLibs:
            boostlib = "boost_" + b
            conf.FindSysLibDep(
                boostlib,
                [boostlib + suffix for suffix in boostSuffixList],
                language='C++')

    conf.env.Append(CPPDEFINES=['MONGO_HAVE_HEADER_UNISTD_H'])
    conf.CheckLib('rt')
    conf.CheckLib('dl')

    conf.env.Append(CPPDEFINES=['MONGO_HAVE_POSIX_MONOTONIC_CLOCK'])

    if (conf.CheckCXXHeader( "execinfo.h" ) and
        conf.CheckDeclaration('backtrace', includes='#include <execinfo.h>') and
        conf.CheckDeclaration('backtrace_symbols', includes='#include <execinfo.h>') and
        conf.CheckDeclaration('backtrace_symbols_fd', includes='#include <execinfo.h>')):

        conf.env.Append( CPPDEFINES=[ "MONGO_HAVE_EXECINFO_BACKTRACE" ] )

    conf.env["_HAVEPCAP"] = conf.CheckLib( ["pcap", "wpcap"], autoadd=False )

    conf.env['MONGO_BUILD_SASL_CLIENT'] = bool(has_option("use-sasl-client"))
    if conf.env['MONGO_BUILD_SASL_CLIENT'] and not conf.CheckLibWithHeader(
            "sasl2", 
            ["stddef.h","sasl/sasl.h"], 
            "C", 
            "sasl_version_info(0, 0, 0, 0, 0, 0);", 
            autoadd=False ):
        Exit(1)

    # 'tcmalloc' needs to be the last library linked. Please, add new libraries before this 
    # point.
    if get_option('allocator') == 'tcmalloc':
        if has_option("heapcheck"):
            print("--heapcheck does not work with the tcmalloc embedded in the mongodb source tree.")
            Exit(1)
    elif get_option('allocator') == 'system':
        pass
    else:
        print("Invalid --allocator parameter: \"%s\"" % get_option('allocator'))
        Exit(1)

    if has_option("heapcheck"):
        if not debugBuild:
            print( "--heapcheck needs --d or --dd" )
            Exit( 1 )

        if not conf.CheckCXXHeader( "google/heap-checker.h" ):
            print( "--heapcheck neads header 'google/heap-checker.h'" )
            Exit( 1 )

        conf.env.Append( CPPDEFINES=[ "HEAP_CHECKING" ] )
        conf.env.Append( CCFLAGS=["-fno-omit-frame-pointer"] )

    # ask each module to configure itself and the build environment.
    moduleconfig.configure_modules(mongo_modules, conf)

    return conf.Finish()

env = doConfigure( env )

env['PDB'] = '${TARGET.base}.pdb'

def checkErrorCodes():
    import buildscripts.errorcodes as x
    if x.checkErrorCodes() == False:
        print( "next id to use:" + str( x.getNextCode() ) )
        Exit(-1)

checkErrorCodes()

#  ---- Docs ----
def build_docs(env, target, source):
    from buildscripts import docs
    docs.main()

env.Alias("docs", [], [build_docs])
env.AlwaysBuild("docs")

#  ---- astyle ----

def doStyling( env , target , source ):

    res = utils.execsys( "astyle --version" )
    res = " ".join(res)
    if res.count( "2." ) == 0:
        print( "astyle 2.x needed, found:" + res )
        Exit(-1)

    files = utils.getAllSourceFiles() 
    files = filter( lambda x: not x.endswith( ".c" ) , files )

    cmd = "astyle --options=mongo_astyle " + " ".join( files )
    res = utils.execsys( cmd )
    print( res[0] )
    print( res[1] )


env.Alias( "style" , [] , [ doStyling ] )
env.AlwaysBuild( "style" )

# --- lint ----



def doLint( env , target , source ):
    import buildscripts.clang_format
    if not buildscripts.clang_format.lint(None, []):
        raise Exception("clang-format lint errors")

    import buildscripts.lint
    if not buildscripts.lint.run_lint( [ "src/mongo/" ] ):
        raise Exception( "lint errors" )

env.Alias( "lint" , [] , [ doLint ] )
env.AlwaysBuild( "lint" )


#  ----  INSTALL -------

def getSystemInstallName():
    arch_name = processor
    n = arch_name
    if static:
        n += "-static"
    if os.uname()[2].startswith("8."):
        n += "-tiger"

    if len(mongo_modules):
            n += "-" + "-".join(m.name for m in mongo_modules)

    try:
        findSettingsSetup()
        import settings
        if "distmod" in dir(settings):
            n = n + "-" + str(settings.distmod)
    except:
        pass

    dn = GetOption("distmod")
    if dn and len(dn) > 0:
        n = n + "-" + dn

    return n

# This function will add the version.txt file to the source tarball
# so that versioning will work without having the git repo available.
def add_version_to_distsrc(env, archive):
    version_file_path = env.subst("$MONGO_DIST_SRC_PREFIX") + "version.json"
    if version_file_path not in archive:
        version_data = {
            'version': env['MONGO_VERSION'],
            'githash': env['MONGO_GIT_HASH'],
        }
        archive.append_file_contents(
            version_file_path,
            json.dumps(
                version_data,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )
        )

env.AddDistSrcCallback(add_version_to_distsrc)

if has_option('distname'):
    distName = GetOption( "distname" )
else:
    distName = env['MONGO_VERSION']

env['SERVER_DIST_BASENAME'] = 'mongodb-%s-%s' % (getSystemInstallName(), distName)

distFile = "${SERVER_ARCHIVE}"

env['NIX_LIB_DIR'] = nixLibPrefix

#  ---- CONVENIENCE ----

def tabs( env, target, source ):
    from subprocess import Popen, PIPE
    from re import search, match
    diff = Popen( [ "git", "diff", "-U0", "origin", "master" ], stdout=PIPE ).communicate()[ 0 ]
    sourceFile = False
    for line in diff.split( "\n" ):
        if match( "diff --git", line ):
            sourceFile = not not search( "\.(h|hpp|c|cpp)\s*$", line )
        if sourceFile and match( "\+ *\t", line ):
            return True
    return False
env.Alias( "checkSource", [], [ tabs ] )
env.AlwaysBuild( "checkSource" )

def gitPush( env, target, source ):
    import subprocess
    return subprocess.call( [ "git", "push" ] )
env.Alias( "push", [ ".", "smoke", "checkSource" ], gitPush )
env.AlwaysBuild( "push" )


# ---- deploying ---

def s3push(localName, remoteName=None):
    localName = str( localName )

    if isBuildingLatest:
        remotePrefix = utils.getGitBranchString("-") + "-latest"
    else:
        remotePrefix = "-" + distName

    findSettingsSetup()

    import simples3
    import settings

    s = simples3.S3Bucket( settings.bucket , settings.id , settings.key )

    if remoteName is None:
        remoteName = localName

    name = '%s-%s%s' % (remoteName , getSystemInstallName(), remotePrefix)
    lastDotIndex = localName.rfind('.')
    if lastDotIndex != -1:
        name += localName[lastDotIndex:]
    name = name.lower()

    print( "uploading " + localName + " to http://s3.amazonaws.com/" + s.name + "/" + name )
    if dontReplacePackage:
        for ( key , modify , etag , size ) in s.listdir( prefix=name ):
            print( "error: already a file with that name, not uploading" )
            Exit(2)
    s.put( name  , open( localName , "rb" ).read() , acl="public-read" );
    print( "  done uploading!" )

def s3shellpush( env , target , source ):
    s3push( "mongo" , "mongo-shell" )

env.Alias( "s3shell" , [ "mongo" ] , [ s3shellpush ] )
env.AlwaysBuild( "s3shell" )

def s3dist( env , target , source ):
    s3push( str(source[0]) , "mongodb" )

env.AlwaysBuild(env.Alias( "s3dist" , [ '$SERVER_ARCHIVE' ] , [ s3dist ] ))

# --- an uninstall target ---
if len(COMMAND_LINE_TARGETS) > 0 and 'uninstall' in COMMAND_LINE_TARGETS:
    SetOption("clean", 1)
    # By inspection, changing COMMAND_LINE_TARGETS here doesn't do
    # what we want, but changing BUILD_TARGETS does.
    BUILD_TARGETS.remove("uninstall")
    BUILD_TARGETS.append("install")

module_sconscripts = moduleconfig.get_module_sconscripts(mongo_modules)

# The following symbols are exported for use in subordinate SConscript files.
# Ideally, the SConscript files would be purely declarative.  They would only
# import build environment objects, and would contain few or no conditional
# statements or branches.
#
# Currently, however, the SConscript files do need some predicates for
# conditional decision making that hasn't been moved up to this SConstruct file,
# and they are exported here, as well.
Export("env")
Export("get_option")
Export("has_option")
Export("usev8")
Export("v8version v8suffix")
Export('module_sconscripts')
Export("debugBuild optBuild")
Export("s3push")
Export("wiredtiger")

def injectMongoIncludePaths(thisEnv):
    thisEnv.AppendUnique(CPPPATH=['$BUILD_DIR'])
env.AddMethod(injectMongoIncludePaths, 'InjectMongoIncludePaths')

env.Alias("distsrc-tar", env.DistSrc("mongodb-src-${MONGO_VERSION}.tar"))
env.Alias("distsrc-tgz", env.GZip(
    target="mongodb-src-${MONGO_VERSION}.tgz",
    source=["mongodb-src-${MONGO_VERSION}.tar"])
)
env.Alias("distsrc-zip", env.DistSrc("mongodb-src-${MONGO_VERSION}.zip"))
env.Alias("distsrc", "distsrc-tgz")

env.SConscript('src/SConscript', variant_dir='$BUILD_DIR', duplicate=False)

def clean_old_dist_builds(env, target, source):
    prefix = "mongodb-%s" % (processor)
    filenames = sorted(os.listdir("."))
    filenames = [x for x in filenames if x.startswith(prefix)]
    to_keep = [x for x in filenames if x.endswith(".tgz") or x.endswith(".zip")][-2:]
    for filename in [x for x in filenames if x not in to_keep]:
        print("removing %s" % filename)
        try:
            shutil.rmtree(filename)
        except:
            os.remove(filename)

env.Alias("dist_clean", [], [clean_old_dist_builds])
env.AlwaysBuild("dist_clean")

env.Alias('all', ['core', 'tools', 'dbtest', 'unittests', 'file_allocator_bench'])
