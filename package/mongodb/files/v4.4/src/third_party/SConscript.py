# -*- mode: python -*-

import SCons

import libdeps
import json

Import("env usemozjs get_option")
Import("use_libunwind")
Import("wiredtiger")

mozjsSuffix = '-60'
timelibSuffix = '-2018.01'
icuSuffix = '-57.1'
tomcryptSuffix = '-1.18.2'

thirdPartyEnvironmentModifications = {
   'fmt' : {
        'CPPPATH' : ['#src/third_party/fmt/dist/include'],
   },
   's2' : {
        'CPPPATH' : ['#src/third_party/s2'],
   },
   'safeint' : {
        'CPPPATH' : ['#src/third_party/SafeInt'],
        # SAFEINT_USE_INTRINSICS=0 for overflow-safe constexpr multiply. See comment in SafeInt.hpp.
        'CPPDEFINES' : [('SAFEINT_USE_INTRINSICS', 0)],
   },
   'timelib' : {
        'CPPPATH' : ['#/src/third_party/timelib' + timelibSuffix],
   },
   'unwind' : {
   },
}

def injectMozJS(thisEnv):
    thisEnv.InjectThirdParty(libraries=['mozjs'])

    thisEnv.Append(
        CCFLAGS=[
            '-include', 'js-config.h',
            '-include', 'js/RequiredDefines.h',
        ],
        CXXFLAGS=[
            '-Wno-non-virtual-dtor',
            '-Wno-invalid-offsetof',
        ],
    )

    thisEnv.Prepend(CPPDEFINES=[
        'JS_USE_CUSTOM_ALLOCATOR',
        'STATIC_JS_API=1',
    ])

    if get_option('spider-monkey-dbg') == "on":
        thisEnv.Prepend(CPPDEFINES=[
            'DEBUG',
            'JS_DEBUG',
        ])

env.AddMethod(injectMozJS, 'InjectMozJS');

# Valgrind is a header only include as valgrind.h includes everything we need
thirdPartyEnvironmentModifications['valgrind'] = {
    'CPPPATH' : ['#/src/third_party/valgrind-3.14.0/include'],
}

# TODO: figure out if we want to offer system versions of mozjs.  Mozilla
# hasn't offered a source tarball since 24, but in theory they could.
#
thirdPartyEnvironmentModifications['mozjs'] = {
    'CPPPATH' : [
        '#/src/third_party/mozjs' + mozjsSuffix + '/include',
        '#/src/third_party/mozjs' + mozjsSuffix + '/mongo_sources',
        '#/src/third_party/mozjs' + mozjsSuffix + '/platform/' + env["TARGET_ARCH"] + "/" + env["TARGET_OS"] + "/include",
    ],
}

if "tom" in env["MONGO_CRYPTO"]:
    thirdPartyEnvironmentModifications['tomcrypt'] = {
        'CPPPATH' : ['#/src/third_party/tomcrypt' + tomcryptSuffix + '/src/headers'],
    }

# Note that the wiredtiger.h header is generated, so
# we want to look for it in the build directory not
# the source directory.
if wiredtiger:
    thirdPartyEnvironmentModifications['wiredtiger'] = {
        'CPPPATH' : ['$BUILD_DIR/third_party/wiredtiger'],
    }

thirdPartyEnvironmentModifications['asio'] = {
    'CPPPATH' : ['#/src/third_party/asio-master/asio/include'],
}

thirdPartyEnvironmentModifications['abseil-cpp'] = {
    'CPPPATH' : ['#/src/third_party/abseil-cpp-master/abseil-cpp'],
}

thirdPartyEnvironmentModifications['intel_decimal128'] = {
    'CPPPATH' : ['#/src/third_party/IntelRDFPMathLib20U1/LIBRARY'],
}

thirdPartyEnvironmentModifications['kms-message'] = {
    'CPPPATH' : ['#/src/third_party/kms-message/src'],
    'CPPDEFINES' :['KMS_MSG_STATIC']
}

thirdPartyEnvironmentModifications['unwind'] = {
    'SYSLIBDEPS' : [env['LIBDEPS_UNWIND_SYSLIBDEP'], 'lzma'],
}

def injectThirdParty(thisEnv, libraries=[], parts=[]):
    libraries = thisEnv.Flatten([libraries])
    parts = thisEnv.Flatten([parts])
    for lib in libraries:
        mods = thirdPartyEnvironmentModifications.get(lib, None)
        if mods is None:
            continue
        if not parts:
            thisEnv.PrependUnique(**mods)
        else:
            for part in parts:
                thisEnv.PrependUnique({part : mods[part]})

env.AddMethod(injectThirdParty, 'InjectThirdParty')

# In a dynamic build, force everything to depend on shim_allocator, so
# that it topsorts to the end of the list.  We are totally relying on
# the fact that we are altering the env from src/SConscript
if get_option('link-model').startswith("dynamic"):

    for builder_name in ('Program', 'SharedLibrary', 'LoadableModule', 'StaticLibrary'):
        builder = env['BUILDERS'][builder_name]
        base_emitter = builder.emitter

        def add_shim_allocator_hack(target, source, env):

            # If we allowed conftests to become dependent, any TryLink
            # that happened after we made the below modifications would
            # cause the configure steps to try to compile tcmalloc and any
            # of its dependencies. Oops!
            if any('conftest' in str(t) for t in target):
                return target, source

            # It is possible that 'env' isn't a unique
            # OverrideEnvironment, since if you didn't pass any kw args
            # into your builder call, you just reuse the env you were
            # called with. That could mean that we see the same
            # envirnoment here multiple times. But that is really OK,
            # since the operation we are performing would be performed on
            # all of them anyway. The flag serves as a way to disable the
            # auto-injection for the handful of libraries where we must do
            # so to avoid forming a cycle.
            if not env.get('DISABLE_ALLOCATOR_SHIM_INJECTION', False):
                lds = env.get('LIBDEPS', [])
                lds.append('$BUILD_DIR/third_party/shim_allocator')
                env['LIBDEPS'] = lds

            return target, source

        builder.emitter = SCons.Builder.ListEmitter([add_shim_allocator_hack, base_emitter])

env = env.Clone()

murmurEnv = env.Clone()
murmurEnv.InjectThirdParty(libraries=['fmt'])
murmurEnv.SConscript('murmurhash3/SConscript', exports={ 'env' : murmurEnv })


s2Env = env.Clone()
s2Env.InjectThirdParty(libraries=['s2', 'boost', 'abseil-cpp', 'fmt', 'safeint'])
s2Env.InjectMongoIncludePaths()
s2Env.SConscript('s2/SConscript', exports={'env' : s2Env})


if use_libunwind:
    unwindEnv = env.Clone(
        SYSLIBDEPS=[
            env['LIBDEPS_UNWIND_SYSLIBDEP'],
        ])


fmtEnv = env.Clone()
fmtEnv.InjectThirdParty(libraries=['fmt'])
fmtEnv.InjectMongoIncludePaths()
fmtEnv.SConscript('fmt/SConscript', exports={'env' : fmtEnv})
fmtEnv = fmtEnv.Clone(
    LIBDEPS_INTERFACE=[
        'fmt/fmt',
    ])

fmtEnv.Library(
    target="shim_fmt",
    source=[
        'shim_fmt.cpp',
    ])


pcreEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_PCRE_SYSLIBDEP'],
        env['LIBDEPS_PCRECPP_SYSLIBDEP'],
    ])

pcreEnv.Library(
    target="shim_pcrecpp",
    source=[
        'shim_pcrecpp.cc',
    ])


boostEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_BOOST_PROGRAM_OPTIONS_SYSLIBDEP'],
        env['LIBDEPS_BOOST_FILESYSTEM_SYSLIBDEP'],
        env['LIBDEPS_BOOST_SYSTEM_SYSLIBDEP'],
        env['LIBDEPS_BOOST_IOSTREAMS_SYSLIBDEP'],
        env['LIBDEPS_BOOST_THREAD_SYSLIBDEP'],
        env['LIBDEPS_BOOST_LOG_SYSLIBDEP'],
    ])

boostEnv.Library(
    target="shim_boost",
    source=[
        'shim_boost.cpp',
    ])


abseilDirectory = 'abseil-cpp-master'
abseilEnv = env.Clone()
abseilEnv.InjectThirdParty(libraries=['abseil-cpp'])
abseilEnv.SConscript(abseilDirectory + '/SConscript', exports={ 'env' : abseilEnv })
abseilEnv = abseilEnv.Clone(
    LIBDEPS_INTERFACE=[
        abseilDirectory + '/absl_container',
        abseilDirectory + '/absl_hash',
    ])

abseilEnv.Library(
    target="shim_abseil",
    source=[
        'shim_abseil.cpp',
    ])


snappyEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_SNAPPY_SYSLIBDEP'],
    ])

snappyEnv.Library(
    target="shim_snappy",
    source=[
        'shim_snappy.cpp',
    ])


zlibEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_ZLIB_SYSLIBDEP'],
    ])

zlibEnv.Library(
    target="shim_zlib",
    source=[
        'shim_zlib.cpp',
    ])


zstdEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_ZSTD_SYSLIBDEP'],
    ])

zstdEnv.Library(
    target="shim_zstd",
    source=[
        'shim_zstd.cpp',
    ])


benchmarkEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_BENCHMARK_SYSLIBDEP'],
    ])

benchmarkEnv.Library(
    target="shim_benchmark",
    source=[
        'shim_benchmark.cpp',
    ])


if usemozjs:
    mozjsEnv = env.Clone()
    mozjsEnv.SConscript('mozjs' + mozjsSuffix + '/SConscript', exports={'env' : mozjsEnv })
    mozjsEnv = mozjsEnv.Clone(
        LIBDEPS_INTERFACE=[
            'mozjs' + mozjsSuffix + '/mozjs',
            'shim_zlib',
        ])

    mozjsEnv.Library(
        target="shim_mozjs",
        source=[
            'shim_mozjs.cpp',
        ])


if "tom" in env["MONGO_CRYPTO"]:
    tomcryptEnv = env.Clone()
    tomcryptEnv.SConscript('tomcrypt' + tomcryptSuffix + '/SConscript', exports={'env' : tomcryptEnv })
    tomcryptEnv = tomcryptEnv.Clone(
        LIBDEPS_INTERFACE=[
            'tomcrypt' + tomcryptSuffix + '/tomcrypt',
        ])

    tomcryptEnv.Library(
        target="shim_tomcrypt",
        source=[
            'shim_tomcrypt.cpp',
        ])

gperftoolsEnv = env
if gperftoolsEnv['MONGO_ALLOCATOR'] in ["tcmalloc", "tcmalloc-experimental"]:
    gperftoolsEnv = env.Clone(
        SYSLIBDEPS=[
            env['LIBDEPS_TCMALLOC_SYSLIBDEP'],
        ])

gperftoolsEnv.Library(
    target="shim_allocator",
    source=[
        "shim_allocator.cpp",
    ],
    DISABLE_ALLOCATOR_SHIM_INJECTION=True,
)


stemmerEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_STEMMER_SYSLIBDEP'],
    ])

stemmerEnv.Library(
    target="shim_stemmer",
    source=[
        'shim_stemmer.cpp'
    ])


yamlEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_YAML_SYSLIBDEP'],
    ])

yamlEnv.Library(
    target="shim_yaml",
    source=[
        'shim_yaml.cpp',
    ])


timelibEnv = env.Clone()
timelibEnv.InjectThirdParty(libraries=['timelib'])
timelibEnv.SConscript('timelib' + timelibSuffix + '/SConscript', exports={ 'env' : timelibEnv })
timelibEnv = timelibEnv.Clone(
    LIBDEPS_INTERFACE=[
        'timelib' + timelibSuffix + '/timelib',
    ])

timelibEnv.Library(
    target='shim_timelib',
    source=[
        'shim_timelib.cpp',
    ])


if wiredtiger:
    wiredtigerEnv = env.Clone()
    wiredtigerEnv.InjectThirdParty(libraries=['wiredtiger'])
    wiredtigerEnv.SConscript('wiredtiger/SConscript', exports={ 'env' : wiredtigerEnv })
    wiredtigerEnv = wiredtigerEnv.Clone(
        LIBDEPS_INTERFACE=[
                'wiredtiger/wiredtiger',
        ])

    wiredtigerEnv.Library(
        target="shim_wiredtiger",
        source=[
            'shim_wiredtiger.cpp'
        ])


asioEnv = env.Clone()
asioEnv.InjectThirdParty(libraries=['asio'])
asioEnv.SConscript('asio-master/SConscript', exports={ 'env' : asioEnv })
asioEnv = asioEnv.Clone(
    LIBDEPS_INTERFACE=[
        'asio-master/asio',
    ])

asioEnv.Library(
    target="shim_asio",
    source=[
        'shim_asio.cpp'
    ])


intelDecimal128Env = env.Clone()
intelDecimal128Env.InjectThirdParty(libraries=['intel_decimal128'])
intelDecimal128Env.SConscript('IntelRDFPMathLib20U1/SConscript', exports={ 'env' : intelDecimal128Env })
intelDecimal128Env = intelDecimal128Env.Clone(
LIBDEPS_INTERFACE=[
    'IntelRDFPMathLib20U1/intel_decimal128',
])

intelDecimal128Env.Library(
    target="shim_intel_decimal128",
    source=[
	'shim_intel_decimal128.cpp'
    ])


icuEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_ICUDATA_SYSLIBDEP'],
        env['LIBDEPS_ICUI18N_SYSLIBDEP'],
        env['LIBDEPS_ICUUC_SYSLIBDEP'],
    ])
    
icuEnv.Library(
    target='shim_icu',
    source=[
        'shim_icu.cpp',
    ])


kmsEnv = env.Clone()
kmsEnv.InjectThirdParty(libraries=['kms-message'])
kmsEnv.SConscript('kms-message/SConscript', exports={ 'env' : kmsEnv })
kmsEnv = kmsEnv.Clone(
    LIBDEPS_INTERFACE=[
        'kms-message/kms-message',
    ])

kmsEnv.Library(
    target="shim_kms_message",
    source=[
        'shim_kms_message.cpp',
    ])

