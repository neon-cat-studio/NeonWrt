# -*- mode: python; -*-

import libdeps

Import("env")
Import("get_option")

env = env.Clone()


if get_option('install-mode') == 'hygienic':
    env.AutoInstall(
        'share/doc/mongo_embedded',
        source=[
            '#/LICENSE-Community.txt',
            '#/distsrc/THIRD-PARTY-NOTICES',
            '../LICENSE-Embedded.txt',
        ],
        INSTALL_ALIAS=[
            'embedded-dev',
        ],
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
    INSTALL_ALIAS=[
        'embedded-dev',
    ],
)

if get_option('install-mode') == 'hygienic':
    env.AutoInstall(
        'include/mongo_embedded/v1/mongo_embedded',
        source=['mongo_embedded.h'],
        INSTALL_ALIAS=[
            'embedded-dev',
        ],
    )

yamlEnv = env.Clone()
yamlEnv.InjectThirdPartyIncludePaths(libraries=['yaml'])

if get_option('link-model') != 'dynamic-sdk':
    mongoEmbeddedTest = yamlEnv.Program(
        target='mongo_embedded_test',
        source=[
            'mongo_embedded_test.cpp',
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/base',
            '$BUILD_DIR/mongo/db/commands/test_commands_enabled',
            '$BUILD_DIR/mongo/db/server_options_core',
            '$BUILD_DIR/mongo/rpc/protocol',
            '$BUILD_DIR/mongo/unittest/unittest',
            '$BUILD_DIR/mongo/util/net/network',
            '$BUILD_DIR/mongo/util/options_parser/options_parser',
            'mongo_embedded',
        ],
        INSTALL_ALIAS=[
            'embedded-test',
        ],
    )

    env.RegisterUnitTest(mongoEmbeddedTest[0])