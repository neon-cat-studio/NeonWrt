# -*- mode: python -*-

Import('env')

env = env.Clone()

# Contains only the core ConnectionString functionality, *not* the ability to call connect() and
# return a DBClientBase* back. For that you need to link against the 'clientdriver_network' library.
env.Library(
    target='connection_string',
    source=[
        'connection_string.cpp',
        'mongo_uri.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/util/net/network',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/util/dns_query',
    ],
)

env.CppUnitTest(
    target='connection_string_test',
    source=[
        'connection_string_test.cpp',
    ],
    LIBDEPS=[
        'connection_string',
    ],
)

env.CppUnitTest(
    target='mongo_uri_test',
    source=[
        'mongo_uri_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/transport/transport_layer_egress_init',
        '$BUILD_DIR/mongo/db/service_context_test_fixture',
        'clientdriver_network',
    ],
)

env.Library(
    target=[
        'read_preference',
    ],
    source=[
        'read_preference.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/bson/util/bson_extract',
        '$BUILD_DIR/mongo/db/service_context'
    ],
)

env.CppUnitTest(
    target=[
        'read_preference_test',
    ],
    source=[
        'read_preference_test.cpp',
    ],
    LIBDEPS=[
        'read_preference',
    ],
)

saslClientEnv = env.Clone()
saslLibs = []
saslClientSource = [
    'native_sasl_client_session.cpp',
    'sasl_client_authenticate.cpp',
    'sasl_client_authenticate_impl.cpp',
    'sasl_client_conversation.cpp',
    'sasl_client_session.cpp',
    'sasl_plain_client_conversation.cpp',
    'sasl_scram_client_conversation.cpp',
]

# Add in actual sasl dependencies if sasl is enabled, otherwise
# leave library empty so other targets can link to it unconditionally
# without needing to first test MONGO_BUILD_SASL_CLIENT.
if env['MONGO_BUILD_SASL_CLIENT']:
    saslClientSource.extend([
        'cyrus_sasl_client_session.cpp',
        'sasl_sspi.cpp',
        'sasl_sspi_options.cpp',
    ])

    saslLibs.extend(['sasl2'])

saslClientEnv.Library(
    target='sasl_client',
    source=saslClientSource,
    LIBDEPS=[
        '$BUILD_DIR/mongo/base/secure_allocator',
        '$BUILD_DIR/mongo/bson/util/bson_extract',
        '$BUILD_DIR/mongo/executor/remote_command',
        '$BUILD_DIR/mongo/rpc/command_status',
        '$BUILD_DIR/mongo/rpc/metadata',
        '$BUILD_DIR/mongo/util/icu',
        '$BUILD_DIR/mongo/util/md5',
        '$BUILD_DIR/mongo/util/net/network',
    ],
    SYSLIBDEPS=saslLibs,
)

env.Library(
    target='authentication',
    source=[
        'authenticate.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/bson/util/bson_extract',
        '$BUILD_DIR/mongo/executor/remote_command',
        'sasl_client'
    ],
)

env.CppUnitTest(
    target=[
        'authenticate_test',
    ],
    source=[
        'authenticate_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/rpc/command_status',
        '$BUILD_DIR/mongo/util/net/network',
        '$BUILD_DIR/mongo/util/md5',
        'authentication',
    ],
)

env.Library(
    target='client_query',
    source=[
        'query.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        'read_preference',
    ],
)

clientDriverEnv = env.Clone()
clientDriverEnv.InjectThirdPartyIncludePaths('asio')

clientDriverEnv.Library(
    target='clientdriver_minimal',
    source=[
        'dbclient.cpp',
        'dbclientcursor.cpp',
        'index_spec.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/db/dbmessage',
        '$BUILD_DIR/mongo/db/query/command_request_response',
        '$BUILD_DIR/mongo/db/query/query_request',
        '$BUILD_DIR/mongo/db/wire_version',
        '$BUILD_DIR/mongo/rpc/command_status',
        '$BUILD_DIR/mongo/rpc/rpc',
        '$BUILD_DIR/mongo/s/common_s',
        'authentication',
        'client_query',
        'connection_string',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/auth/internal_user_auth',
        '$BUILD_DIR/mongo/util/net/ssl_manager',
    ],
)

clientDriverEnv.Library(
    target='clientdriver_network',
    source=[
        'connection_string_connect.cpp',
        'mongo_uri_connect.cpp',
        'connpool.cpp',
        'dbclient_connection.cpp',
        'dbclient_rs.cpp',
        'global_conn_pool.cpp',
        'replica_set_monitor.cpp',
        'replica_set_monitor_manager.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/db/write_concern_options',
        '$BUILD_DIR/mongo/executor/connection_pool_stats',
        '$BUILD_DIR/mongo/executor/network_interface_factory',
        '$BUILD_DIR/mongo/executor/network_interface_thread_pool',
        '$BUILD_DIR/mongo/executor/thread_pool_task_executor',
        '$BUILD_DIR/mongo/util/background_job',
        '$BUILD_DIR/mongo/util/md5',
        '$BUILD_DIR/mongo/util/net/network',
        'clientdriver_minimal',
        'read_preference',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/commands/test_commands_enabled',
        '$BUILD_DIR/mongo/transport/message_compressor',
    ]
)

env.CppIntegrationTest(
    target='connpool_integration_test',
    source=[
        'connpool_integration_test.cpp',
    ],
    LIBDEPS=[
        'clientdriver_network',
        '$BUILD_DIR/mongo/transport/transport_layer_egress_init',
        '$BUILD_DIR/mongo/util/version_impl',
    ],
)

env.Library(
    target='async_client',
    source=[
        'async_client.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/db/wire_version',
        '$BUILD_DIR/mongo/rpc/command_status',
        '$BUILD_DIR/mongo/rpc/rpc',
        '$BUILD_DIR/mongo/transport/transport_layer_common',
        '$BUILD_DIR/mongo/util/net/ssl_manager',
        'authentication',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/auth/internal_user_auth',
        '$BUILD_DIR/mongo/db/commands/test_commands_enabled',
        '$BUILD_DIR/mongo/executor/egress_tag_closer_manager',
        '$BUILD_DIR/mongo/transport/message_compressor',
        '$BUILD_DIR/mongo/util/net/ssl_manager',
    ],
)

env.Library(
    target='connection_pool',
    source=[
        'connection_pool.cpp',
    ],
    LIBDEPS=[
        'clientdriver_network',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/auth/internal_user_auth',
    ],
)

env.Library(
    target='remote_command_targeter',
    source=[
        'remote_command_targeter_factory_impl.cpp',
        'remote_command_targeter_rs.cpp',
        'remote_command_targeter_standalone.cpp',
    ],
    LIBDEPS=[
        'clientdriver_network',
        '$BUILD_DIR/mongo/db/service_context',
    ],
)

env.Library(
    target='remote_command_targeter_mock',
    source=[
        'remote_command_targeter_mock.cpp',
        'remote_command_targeter_factory_mock.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/util/net/network',
        '$BUILD_DIR/mongo/s/coreshard',
    ],
)

env.CppUnitTest(
    target='replica_set_monitor_test',
    source=[
        'replica_set_monitor_node_test.cpp',
        'replica_set_monitor_read_preference_test.cpp',
        'replica_set_monitor_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/db/write_concern_options',
        'clientdriver_network',
    ],
)

env.CppUnitTest('dbclient_rs_test',
                ['dbclient_rs_test.cpp'],
                LIBDEPS=[
                    'clientdriver_network',
                    '$BUILD_DIR/mongo/dbtests/mocklib',
                ],
)

env.CppUnitTest(
    target='index_spec_test',
    source=[
        'index_spec_test.cpp',
    ],
    LIBDEPS=[
        'clientdriver_minimal',
    ],
)

env.Library(
    target='fetcher',
    source=[
        'fetcher.cpp',
    ],
    LIBDEPS=[
        'remote_command_retry_scheduler',
        '$BUILD_DIR/mongo/executor/task_executor_interface',
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/db/namespace_string',
        '$BUILD_DIR/mongo/rpc/command_status',
    ],
)

env.CppUnitTest(
    target='fetcher_test',
    source='fetcher_test.cpp',
    LIBDEPS=[
        'fetcher',
        '$BUILD_DIR/mongo/db/auth/authmocks',
        '$BUILD_DIR/mongo/executor/thread_pool_task_executor_test_fixture',
    ],
)

env.Library(
    target='remote_command_retry_scheduler',
    source=[
        'remote_command_retry_scheduler.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/executor/task_executor_interface',
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='remote_command_retry_scheduler_test',
    source='remote_command_retry_scheduler_test.cpp',
    LIBDEPS=[
        'remote_command_retry_scheduler',
        '$BUILD_DIR/mongo/executor/thread_pool_task_executor_test_fixture',
        '$BUILD_DIR/mongo/unittest/task_executor_proxy',
    ],
)
