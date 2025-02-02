# -*- mode: python -*-

Import('env')
Import("get_option")

env = env.Clone()

env.SConscript(
    dirs=['sdam'],
    exports=['env']
)

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

env.Library(
    target=[
        'read_preference',
    ],
    source=[
        'read_preference.cpp',
        env.Idlc('hedging_mode.idl')[0],
        env.Idlc('read_preference.idl')[0],
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/bson/util/bson_extract',
        '$BUILD_DIR/mongo/db/service_context'
    ],
)

env.Library(
    target=[
        'sasl_aws_common',
    ],
    source=[
        env.Idlc('sasl_aws_protocol_common.idl')[0],
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/idl/idl_parser',
        '$BUILD_DIR/mongo/db/server_options_core', # For object_check.h
    ],
)

kmsEnv = env.Clone()

kmsEnv.InjectThirdParty(libraries=['kms-message'])

kmsEnv.Library(
    target=[
        'sasl_aws_client',
    ],
    source=[
        'sasl_aws_client_protocol.cpp',
        env.Idlc('sasl_aws_client_protocol.idl')[0],
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/third_party/shim_kms_message',
        '$BUILD_DIR/mongo/idl/idl_parser',
        '$BUILD_DIR/mongo/db/server_options_core', # For object_check.h
        'sasl_aws_common',
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

if get_option('ssl') == 'on':
    saslClientSource.extend([
        'sasl_aws_client_conversation.cpp',
        env.Idlc('sasl_aws_client_options.idl')[0],
    ])

# Add in actual sasl dependencies if sasl is enabled, otherwise
# leave library empty so other targets can link to it unconditionally
# without needing to first test MONGO_BUILD_SASL_CLIENT.
if env['MONGO_BUILD_SASL_CLIENT']:
    saslClientSource.extend([
        'cyrus_sasl_client_session.cpp',
        'sasl_sspi.cpp',
        'sasl_sspi_options.cpp',
        env.Idlc('sasl_sspi_options.idl')[0],
    ])

    saslLibs.extend(['sasl2'])

saslClientEnv.Library(
    target='sasl_client',
    source=saslClientSource,
    LIBDEPS=[
        "sasl_aws_client" if get_option('ssl') == 'on' else '',
        '$BUILD_DIR/mongo/base/secure_allocator',
        '$BUILD_DIR/mongo/bson/util/bson_extract',
        '$BUILD_DIR/mongo/executor/remote_command',
        '$BUILD_DIR/mongo/rpc/command_status',
        '$BUILD_DIR/mongo/rpc/metadata',
        '$BUILD_DIR/mongo/util/icu',
        '$BUILD_DIR/mongo/util/md5',
        '$BUILD_DIR/mongo/util/net/network',
        '$BUILD_DIR/mongo/util/options_parser/options_parser',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/util/net/http_client',
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
    LIBDEPS_PRIVATE=[
        'connection_string',
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
clientDriverEnv.InjectThirdParty('asio')

clientDriverEnv.Library(
    target='clientdriver_minimal',
    source=[
        'dbclient_base.cpp',
        'dbclient_cursor.cpp',
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
        env.Idlc('global_conn_pool.idl')[0],
        'replica_set_change_notifier.cpp',
        'replica_set_monitor.cpp',
        'replica_set_monitor_manager.cpp',
        'scanning_replica_set_monitor.cpp',
        'streamable_replica_set_monitor.cpp',
        'streamable_replica_set_monitor_query_processor.cpp',
        'streamable_replica_set_monitor_error_handler.cpp',
        'server_is_master_monitor.cpp',
        'server_ping_monitor.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/db/write_concern_options',
        '$BUILD_DIR/mongo/executor/connection_pool_stats',
        '$BUILD_DIR/mongo/executor/network_interface',
        '$BUILD_DIR/mongo/executor/network_interface_factory',
        '$BUILD_DIR/mongo/executor/network_interface_thread_pool',
        '$BUILD_DIR/mongo/executor/thread_pool_task_executor',
        '$BUILD_DIR/mongo/util/background_job',
        '$BUILD_DIR/mongo/util/md5',
        '$BUILD_DIR/mongo/util/net/network',
        'replica_set_monitor_server_parameters',
		'$BUILD_DIR/mongo/client/sdam/sdam',
        'clientdriver_minimal',
        'read_preference',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/commands/test_commands_enabled',
        '$BUILD_DIR/mongo/transport/message_compressor',
        '$BUILD_DIR/mongo/util/net/ssl_manager',
    ]
)

env.Library(
    target='replica_set_monitor_server_parameters',
    source=[
        'replica_set_monitor_server_parameters.cpp',
        env.Idlc('replica_set_monitor_server_parameters.idl')[0],
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/idl/server_parameter',
    ]
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
    target='client_test',
    source=[
        'authenticate_test.cpp',
        'connection_string_test.cpp',
        'dbclient_cursor_test.cpp',
        'fetcher_test.cpp',
        'index_spec_test.cpp',
        'mongo_uri_test.cpp',
        'read_preference_test.cpp',
        'remote_command_retry_scheduler_test.cpp',
        'replica_set_monitor_server_parameters_test.cpp',
        'scanning_replica_set_monitor_internal_test.cpp',
        'scanning_replica_set_monitor_read_preference_test.cpp',
        'scanning_replica_set_monitor_scan_test.cpp',
        'scanning_replica_set_monitor_test_concurrent.cpp',
        'scanning_replica_set_monitor_test_fixture.cpp',
        'server_is_master_monitor_expedited_test.cpp',
        'server_is_master_monitor_test.cpp',
        'server_ping_monitor_test.cpp',
        'streamable_replica_set_monitor_error_handler_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/client/sdam/sdam',
        '$BUILD_DIR/mongo/client/sdam/sdam_test',
        '$BUILD_DIR/mongo/db/auth/authmocks',
        '$BUILD_DIR/mongo/db/service_context_test_fixture',
        '$BUILD_DIR/mongo/db/write_concern_options',
        '$BUILD_DIR/mongo/dbtests/mocklib',
        '$BUILD_DIR/mongo/executor/network_interface_mock',
        '$BUILD_DIR/mongo/executor/task_executor_test_fixture',
        '$BUILD_DIR/mongo/executor/thread_pool_task_executor_test_fixture',
        '$BUILD_DIR/mongo/rpc/command_status',
        '$BUILD_DIR/mongo/transport/transport_layer_egress_init',
        '$BUILD_DIR/mongo/unittest/task_executor_proxy',
        '$BUILD_DIR/mongo/util/md5',
        '$BUILD_DIR/mongo/util/net/network',
        'authentication',
        'clientdriver_minimal',
        'clientdriver_network',
        'connection_string',
        'fetcher',
        'read_preference',
        'remote_command_retry_scheduler',
        'replica_set_monitor_protocol_test_util',
    ],
)

env.CppIntegrationTest(
    target='replica_set_monitor_integration_test',
    source=[
        'replica_set_monitor_integration_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/client/clientdriver_network',
        '$BUILD_DIR/mongo/db/wire_version',
        '$BUILD_DIR/mongo/executor/network_interface_factory',
        '$BUILD_DIR/mongo/executor/network_interface_thread_pool',
        '$BUILD_DIR/mongo/executor/thread_pool_task_executor',
        '$BUILD_DIR/mongo/transport/transport_layer_egress_init',
        '$BUILD_DIR/mongo/util/concurrency/thread_pool',
        '$BUILD_DIR/mongo/util/version_impl',
    ],
)

env.Library(
    target='replica_set_monitor_protocol_test_util',
    source=[
        'replica_set_monitor_protocol_test_util.cpp',
    ],
    LIBDEPS=[
        'clientdriver_network',
    ],
)

# Cannot be combined with the above unit test due to an explicit call to
# ReplicaSetMonitor::disableRefreshRetries_forTest.
env.CppUnitTest(
    target='client_rs_test',
    source=[
        'dbclient_rs_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/dbtests/mocklib',
        'clientdriver_network',
        'replica_set_monitor_protocol_test_util',
    ],
)

# The following two tests cannot be combined because the second one
# needs to be filtered out for the repl and sharding variants of the
# integration tests.
env.CppIntegrationTest(
    target='client_connpool_integration_test',
    source=[
        'connpool_integration_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/transport/transport_layer_egress_init',
        '$BUILD_DIR/mongo/util/version_impl',
        'clientdriver_network',
    ],
)

env.CppIntegrationTest(
    target='client_dbclient_connection_integration_test',
    source=[
        'dbclient_connection_integration_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/transport/transport_layer_egress_init',
        '$BUILD_DIR/mongo/util/version_impl',
        'clientdriver_network',
    ],
)

env.Library(
    target='dbclient_mockcursor',
    source=[
        'dbclient_mockcursor.cpp'
    ],
    LIBDEPS_PRIVATE=[
        'clientdriver_minimal'
    ],
)
