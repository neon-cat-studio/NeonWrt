# -*- mode: python -*-

Import("env usev8 v8suffix")
Import("wiredtiger")

thirdPartyIncludePathList = [
    ('s2', '#/src/third_party/s2'),
    ('tz', '#/src/third_party/tz'),
]

thirdPartyIncludePathList.append(
    ('v8', '#/src/third_party/v8' + v8suffix + '/include'))

# Note that the wiredtiger header is generated, so
# we want to look for it in the build directory not
# the source directory.
if wiredtiger:
    thirdPartyIncludePathList.append(
        ('wiredtiger', '$BUILD_DIR/third_party/wiredtiger'))

def injectAllThirdPartyIncludePaths(thisEnv):
    thisEnv.PrependUnique(CPPPATH=[entry[1] for entry in thirdPartyIncludePathList])

def injectThirdPartyIncludePaths(thisEnv, libraries):
    thisEnv.PrependUnique(CPPPATH=[
        entry[1] for entry in thirdPartyIncludePathList if entry[0] in libraries])

env.AddMethod(injectAllThirdPartyIncludePaths, 'InjectAllThirdPartyIncludePaths')
env.AddMethod(injectThirdPartyIncludePaths, 'InjectThirdPartyIncludePaths')


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
        env['LIBDEPS_BOOST_THREAD_SYSLIBDEP'],
        env['LIBDEPS_BOOST_SYSTEM_SYSLIBDEP'],
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

if usev8:
    v8Env = env.Clone()
    v8Env.InjectThirdPartyIncludePaths(libraries=['v8'])
    v8Env.SConscript('v8' + v8suffix + '/SConscript', exports={'env' : v8Env })
    v8Env = v8Env.Clone(
        LIBDEPS=[
            'v8' + v8suffix + '/v8'
        ])

    v8Env.Library(
        target="shim_v8",
        source=[
            'shim_v8.cpp',
        ])


gperftoolsEnv = env
if (GetOption("allocator") == "tcmalloc"):
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


tzEnv = env.Clone()

tzEnv.Library(
    target='shim_tz',
    source=[
        'shim_tz.cpp',
    ])


if wiredtiger:
    wiredtigerEnv = env.Clone()
    wiredtigerEnv.InjectThirdPartyIncludePaths(libraries=['wiredtiger'])
    wiredtigerEnv.SConscript('wiredtiger/SConscript', exports={ 'env' : wiredtigerEnv })
    wiredtigerEnv = wiredtigerEnv.Clone(
        LIBDEPS=[
            'wiredtiger/wiredtiger',
        ])

    wiredtigerEnv.Library(
        target="shim_wiredtiger",
        source=[
            'shim_wiredtiger.cpp'
        ])


