# -*- mode: python; -*-

import libdeps

Import("env")
Import("get_option")

env = env.Clone()

if not env['MONGO_HAVE_LIBMONGOC']:
    Return()

if get_option('install-mode') == 'hygienic':
    env.AutoInstall(
        'share/doc/mongoc_embedded',
        source=[
            '#/LICENSE-Community.txt',
            '../LICENSE-Embedded.txt',
        ],
        INSTALL_ALIAS=[
            'embedded-dev',
        ],
    )

def create_mongoc_env(env):
    mongocEnv = env.Clone()
    if mongocEnv['MONGO_HAVE_LIBMONGOC'] == "framework":
        mongocEnv.AppendUnique(FRAMEWORKS=['bson', 'mongoc'])
    else:
        mongocEnv.AppendUnique(LIBS=['bson-1.0', 'mongoc-1.0'])
    return mongocEnv

mongocEmbeddedEnv = create_mongoc_env(env)

mongocEmbeddedEnv.AppendUnique(
    CPPDEFINES=[
        'MONGOC_EMBEDDED_COMPILING',
     ],
)

if get_option('link-model') == 'static':
    mongocEmbeddedEnv.AppendUnique(
        CPPDEFINES=[
            'MONGOC_EMBEDDED_STATIC',
        ],
    )

# Please see the note in ../mongo_embedded/SConscript about how to
# interpret and adjust the current and compatibility versinos.
mongocEmbeddedEnv.AppendUnique(
    SHLINKFLAGS=[
        '$MONGO_EXPORT_FILE_SHLINKFLAGS',
    ],
)

mongocEmbeddedTargets = mongocEmbeddedEnv.Library(
    target='mongoc_embedded',
    source=[
        'mongoc_embedded.cpp',
    ],
    LIBDEPS=[
        # No LIBDEPS or LIBDEPS_PRIVATE to mongo libraries are allowed in this library. They would get duplicated in mongo_embedded_capi.
        '$BUILD_DIR/mongo/embedded/mongo_embedded/mongo_embedded',
    ],
    INSTALL_ALIAS=[
        'embedded-dev',
    ],
)

if get_option('install-mode') == 'hygienic':
    env.AutoInstall(
        'include/mongoc_embedded/v1/mongoc_embedded',
        source=['mongoc_embedded.h'],
        INSTALL_ALIAS=[
            'embedded-dev',
        ],
    )

yamlEnv = env.Clone()
yamlEnv.InjectThirdPartyIncludePaths(libraries=['yaml'])

if get_option('link-model') != 'dynamic-sdk':
    mongocEmbeddedTestEnv = create_mongoc_env(yamlEnv)
    clientTest = mongocEmbeddedTestEnv.Program(
        target='mongoc_embedded_test',
        source=[
            'mongoc_embedded_test.cpp',
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/base',
            '$BUILD_DIR/mongo/db/server_options_core',
            '$BUILD_DIR/mongo/unittest/unittest',
            '$BUILD_DIR/mongo/util/options_parser/options_parser',
            'mongoc_embedded',
        ],
        INSTALL_ALIAS=[
            'embedded-test',
        ],
    )

    env.RegisterUnitTest(clientTest[0]);
