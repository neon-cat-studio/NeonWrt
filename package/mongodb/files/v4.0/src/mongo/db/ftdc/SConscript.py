# -*- mode: python -*-
Import("env")

env = env.Clone()

ftdcEnv = env.Clone()
ftdcEnv.InjectThirdPartyIncludePaths(libraries=['zlib'])

ftdcEnv.Library(
    target='ftdc',
    source=[
        'block_compressor.cpp',
        'collector.cpp',
        'compressor.cpp',
        'controller.cpp',
        'decompressor.cpp',
        'file_manager.cpp',
        'file_reader.cpp',
        'file_writer.cpp',
        'util.cpp',
        'varint.cpp'
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/bson/util/bson_extract',
        '$BUILD_DIR/mongo/db/server_options_core',
        '$BUILD_DIR/mongo/db/service_context',
        '$BUILD_DIR/third_party/s2/s2', # For VarInt
        '$BUILD_DIR/third_party/shim_zlib',
    ],
)

platform_libs = [
    '$BUILD_DIR/mongo/util/procparser'
]

env.Library(
    target='ftdc_server',
    source=[
        'ftdc_server.cpp',
        'ftdc_system_stats.cpp',
        'ftdc_system_stats_${TARGET_OS}.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/db/commands',
        '$BUILD_DIR/mongo/db/server_parameters',
        '$BUILD_DIR/mongo/util/processinfo',
        'ftdc'
    ] + platform_libs,
)

env.Library(
    target='ftdc_mongod',
    source=[
        'ftdc_commands.cpp',
        'ftdc_mongod.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/db/repl/repl_coordinator_interface',
        '$BUILD_DIR/mongo/db/storage/storage_options',
        'ftdc_server'
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/auth/auth',
        '$BUILD_DIR/mongo/db/auth/authprivilege',
    ],
)

env.Library(
    target='ftdc_mongos',
    source=[
        'ftdc_mongos.cpp',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/client/clientdriver_minimal',
        '$BUILD_DIR/mongo/executor/task_executor_pool',
        '$BUILD_DIR/mongo/s/grid',
        'ftdc_server',
    ],
)

env.CppUnitTest(
    target='ftdc_test',
    source=[
        'compressor_test.cpp',
        'controller_test.cpp',
        'file_manager_test.cpp',
        'file_writer_test.cpp',
        'ftdc_test.cpp',
        'util_test.cpp',
        'varint_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/db/service_context_test_fixture',
        '$BUILD_DIR/mongo/util/clock_source_mock',
        'ftdc',
    ],
)
