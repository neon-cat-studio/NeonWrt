# -*- mode: python -*-

import libdeps

Import("env usemozjs get_option")
Import("wiredtiger")
Import("mobile_se")

mozjsSuffix = '-45'
timelibSuffix = '-2018.01alpha1'
tomcryptSuffix = '-1.18.1'
icuSuffix = '-57.1'
sqliteSuffix = '-amalgamation-3190300'

thirdPartyIncludePathList = [
    ('s2', '#/src/third_party/s2'),
    ('timelib', '#/src/third_party/timelib' + timelibSuffix),
]

# TODO: figure out if we want to offer system versions of mozjs.  Mozilla
# hasn't offered a source tarball since 24, but in theory they could.
#
thirdPartyIncludePathList.append(
    ('mozjs', ['#/src/third_party/mozjs' + mozjsSuffix + '/include',
                '#/src/third_party/mozjs' + mozjsSuffix + '/mongo_sources',
                '#/src/third_party/mozjs' + mozjsSuffix + '/platform/' + env["TARGET_ARCH"] + "/" + env["TARGET_OS"] + "/include",
    ]))

if "tom" in env["MONGO_CRYPTO"]:
    thirdPartyIncludePathList.append(
        ('tomcrypt', ['#/src/third_party/tomcrypt' + tomcryptSuffix + '/src/headers',
    ]))

# Note that the wiredtiger.h header is generated, so
# we want to look for it in the build directory not
# the source directory.
if wiredtiger:
    thirdPartyIncludePathList.append(
        ('wiredtiger', '$BUILD_DIR/third_party/wiredtiger'))

thirdPartyIncludePathList.append(
    ('asio', '#/src/third_party/asio-master/asio/include'))

thirdPartyIncludePathList.append(
    ('valgrind', '#/src/third_party/valgrind-3.11.0/include'))
    
thirdPartyIncludePathList.append(
    ('intel_decimal128', '#/src/third_party/IntelRDFPMathLib20U1/LIBRARY'))

def injectAllThirdPartyIncludePaths(thisEnv):
    thisEnv.PrependUnique(CPPPATH=[entry[1] for entry in thirdPartyIncludePathList])

def injectThirdPartyIncludePaths(thisEnv, libraries):
    thisEnv.PrependUnique(CPPPATH=[
        entry[1] for entry in thirdPartyIncludePathList if entry[0] in libraries])

env.AddMethod(injectAllThirdPartyIncludePaths, 'InjectAllThirdPartyIncludePaths')
env.AddMethod(injectThirdPartyIncludePaths, 'InjectThirdPartyIncludePaths')

env = env.Clone()

murmurEnv = env.Clone()
murmurEnv.SConscript('murmurhash3/SConscript', exports={ 'env' : murmurEnv })


s2Env = env.Clone()
s2Env.InjectThirdPartyIncludePaths(libraries=['s2', 'boost'])
s2Env.InjectMongoIncludePaths()
s2Env.SConscript('s2/SConscript', exports={'env' : s2Env})


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
    ])

boostEnv.Library(
    target="shim_boost",
    source=[
        'shim_boost.cpp',
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
if (gperftoolsEnv['MONGO_ALLOCATOR'] == "tcmalloc"):
    gperftoolsEnv = env.Clone(
        SYSLIBDEPS=[
            env['LIBDEPS_TCMALLOC_SYSLIBDEP'],
        ])

gperftoolsEnv.Library(
    target="shim_allocator",
    source=[
        "shim_allocator.cpp",
    ])


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

timelibEnv = env.Clone();
timelibEnv.InjectThirdPartyIncludePaths(libraries=['timelib'])
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
    wiredtigerEnv.InjectThirdPartyIncludePaths(libraries=['wiredtiger'])
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

sqliteEnv = env.Clone(
    SYSLIBDEPS=[
        env['LIBDEPS_SQLITE_SYSLIBDEP']
    ])

sqliteEnv.Library(
    target='shim_sqlite',
    source=[
        'shim_sqlite.cpp',
    ])

asioEnv = env.Clone()
asioEnv.InjectThirdPartyIncludePaths(libraries=['asio'])
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
intelDecimal128Env.InjectThirdPartyIncludePaths(libraries=['intel_decimal128'])
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

