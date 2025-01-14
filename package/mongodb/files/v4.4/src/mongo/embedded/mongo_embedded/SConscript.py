# -*- mode: python; -*-

import libdeps

Import("env")
Import("get_option")

env = env.Clone()


if get_option('install-mode') == 'hygienic':
    env.AutoInstall(
        '$PREFIX_DOCDIR/mongo_embedded',
        source=[
            '#/LICENSE-Community.txt',
            '../LICENSE-Embedded.txt',
        ],
        AIB_COMPONENT='embedded',
        AIB_ROLE='base',
    )

mongoEmbeddedEnv = env.Clone()
mongoEmbeddedEnv.AppendUnique(
    CPPDEFINES=[
        'MONGO_EMBEDDED_COMPILING',
    ],
)

if get_option('link-model') == 'static':
    mongoEmbeddedEnv.AppendUnique(
        CPPDEFINES=[
            'MONGO_EMBEDDED_STATIC',
        ],
    )
elif get_option('link-model') == 'dynamic-sdk':
    mongoEmbeddedEnv['LIBDEPS_SHLIBEMITTER'] = libdeps.make_libdeps_emitter(
        'SharedArchive',
        libdeps.dependency_visibility_honored
    )

mongoEmbeddedEnv.AppendUnique(
    SHLINKFLAGS=[
        '$MONGO_EXPORT_FILE_SHLINKFLAGS',
    ],
)

mongoEmbeddedTargets = mongoEmbeddedEnv.Library(
    target='mongo_embedded',
    source=[
        'mongo_embedded.cpp',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/service_context',
        '$BUILD_DIR/mongo/rpc/protocol',
        '$BUILD_DIR/mongo/transport/transport_layer_mock',
        '$BUILD_DIR/mongo/embedded/embedded',
    ],
    AIB_COMPONENT='embedded',
)

if get_option('install-mode') == 'hygienic':
    env.AutoInstall(
        '$PREFIX_INCLUDEDIR/mongo_embedded/v1/mongo_embedded',
        source=['mongo_embedded.h'],
        AIB_COMPONENT='embedded',
        AIB_ROLE='dev',
    )

yamlEnv = env.Clone()
yamlEnv.InjectThirdParty(libraries=['yaml'])

if get_option('link-model') != 'dynamic-sdk':
    mongoEmbeddedTest = yamlEnv.CppUnitTest(
        target='mongo_embedded_test',
        source=[
            'mongo_embedded_test.cpp',
            env.Idlc('mongo_embedded_test.idl')[0],
        ],
        LIBDEPS_PRIVATE=[
            '$BUILD_DIR/mongo/base',
            '$BUILD_DIR/mongo/db/commands/test_commands_enabled',
            '$BUILD_DIR/mongo/db/server_options_core',
            '$BUILD_DIR/mongo/rpc/protocol',
            '$BUILD_DIR/mongo/unittest/unittest',
            '$BUILD_DIR/mongo/util/net/network',
            '$BUILD_DIR/mongo/util/options_parser/options_parser',
            'mongo_embedded',
        ],
        UNITTEST_HAS_CUSTOM_MAINLINE=True,
        AIB_COMPONENT='embedded-test',
    )
