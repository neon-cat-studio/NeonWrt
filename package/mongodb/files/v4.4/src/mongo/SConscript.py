# -*- mode: python; -*-

# This SConscript describes build rules for the "mongo" project.

import itertools
import os
import re
import sys
from buildscripts import utils

Import("env")
Import("has_option")
Import("get_option")
Import("usemozjs")
Import("use_libunwind")
Import("wiredtiger")

env = env.Clone()

env.InjectThirdParty('abseil-cpp')

env.InjectMongoIncludePaths()

env.SConscript(
    dirs=[
        'base',
        'bson',
        'client',
        'crypto',
        'db',
        'dbtests',
        'embedded',
        'executor',
        'idl',
        'logger',
        'logv2',
        'platform',
        'rpc',
        's',
        'scripting',
        'shell',
        'stdx',
        'tools',
        'transport',
        'unittest',
        'util',
        'watchdog',
    ],
    exports=[
        'env',
    ],
)

# NOTE: The 'base' library does not really belong here. Its presence
# here is temporary. Do not add to this library, do not remove from
# it, and do not declare other libraries in this file.
baseEnv = env.Clone()

if use_libunwind == True:
    baseEnv.InjectThirdParty('unwind')

stacktrace_impl_cpp = [ File('util/stacktrace_${TARGET_OS_FAMILY}.cpp') ]

baseEnv.Library(
    target='base',
    source=[
        'base/data_range.cpp',
        'base/data_range_cursor.cpp',
        'base/data_type.cpp',
        'base/data_type_string_data.cpp',
        'base/data_type_terminated.cpp',
        'base/error_codes.cpp',
        'base/error_extra_info.cpp',
        'base/global_initializer.cpp',
        'base/global_initializer_registerer.cpp',
        'base/init.cpp',
        'base/initializer.cpp',
        'base/initializer_dependency_graph.cpp',
        'base/parse_number.cpp',
        'base/shim.cpp',
        'base/simple_string_data_comparator.cpp',
        'base/status.cpp',
        'base/string_data.cpp',
        'base/validate_locale.cpp',
        'bson/bson_comparator_interface_base.cpp',
        'bson/bson_depth.cpp',
        'bson/bson_validate.cpp',
        'bson/bsonelement.cpp',
        'bson/bsonmisc.cpp',
        'bson/bsonobj.cpp',
        'bson/bsonobjbuilder.cpp',
        'bson/bsontypes.cpp',
        'bson/json.cpp',
        'bson/oid.cpp',
        'bson/simple_bsonelement_comparator.cpp',
        'bson/simple_bsonobj_comparator.cpp',
        'bson/timestamp.cpp',
        'logger/component_message_log_domain.cpp',
        'logger/console.cpp',
        'logger/log_manager.cpp',
        'logger/logger.cpp',
        'logger/message_event_utf8_encoder.cpp',
        'logger/ramlog.cpp',
        'logger/rotatable_file_manager.cpp',
        'logger/rotatable_file_writer.cpp',
        'logv2/attributes.cpp',
        'logv2/bson_formatter.cpp',
        'logv2/console.cpp',
        'logv2/file_rotate_sink.cpp',
        'logv2/json_formatter.cpp',
        'logv2/log_component.cpp',
        'logv2/log_component_settings.cpp',
        'logv2/log_detail.cpp',
        'logv2/log_domain.cpp',
        'logv2/log_domain_global.cpp',
        'logv2/log_domain_internal.cpp',
        'logv2/log_manager.cpp',
        'logv2/log_severity.cpp',
        'logv2/log_tag.cpp',
        'logv2/log_util.cpp',
        'logv2/plain_formatter.cpp',
        'logv2/shared_access_fstream.cpp',
        'logv2/ramlog.cpp',
        'logv2/redaction.cpp',
        'logv2/text_formatter.cpp',
        'platform/decimal128.cpp',
        'platform/mutex.cpp',
        'platform/posix_fadvise.cpp',
        'platform/process_id.cpp',
        'platform/random.cpp',
        'platform/shared_library.cpp',
        'platform/shared_library_${TARGET_OS_FAMILY}.cpp',
        'platform/stack_locator.cpp',
        'platform/stack_locator_${TARGET_OS}.cpp',
        'platform/strcasestr.cpp',
        'platform/strnlen.cpp',
        'util/allocator.cpp',
        'util/assert_util.cpp',
        'util/base64.cpp',
        'util/boost_assert_impl.cpp',
        'util/concurrency/idle_thread_block.cpp',
        'util/concurrency/thread_name.cpp',
        'util/duration.cpp',
        'util/str_escape.cpp',
        'util/errno_util.cpp',
        'util/exception_filter_win32.cpp',
        'util/exit.cpp',
        'util/file.cpp',
        'util/hex.cpp',
        'util/itoa.cpp',
        'util/platform_init.cpp',
        'util/shell_exec.cpp',
        'util/signal_handlers_synchronous.cpp',
        'util/stacktrace_${TARGET_OS_FAMILY}.cpp',
        'util/stacktrace_json.cpp',
        'util/stacktrace_somap.cpp',
        'util/stacktrace_threads.cpp',
        'util/str.cpp',
        'util/system_clock_source.cpp',
        'util/system_tick_source.cpp',
        'util/text.cpp',
        'util/thread_safety_context.cpp',
        'util/time_support.cpp',
        'util/timer.cpp',
        'util/uuid.cpp',
        'util/version.cpp',
    ],
    # NOTE: This library *must not* depend on any libraries than
    # the ones declared here. Do not add to this list.
    LIBDEPS=[
        '$BUILD_DIR/third_party/murmurhash3/murmurhash3',
        '$BUILD_DIR/third_party/shim_abseil',
        '$BUILD_DIR/third_party/shim_allocator',
        '$BUILD_DIR/third_party/shim_boost',
        '$BUILD_DIR/third_party/shim_fmt',
        '$BUILD_DIR/third_party/shim_intel_decimal128',
        '$BUILD_DIR/third_party/shim_pcrecpp',
        '$BUILD_DIR/third_party/shim_unwind' if use_libunwind else [],
        'boost_assert_shim',
        'stdx/stdx',
        'util/quick_exit',
    ],
    LIBDEPS_PRIVATE=[
        'util/debugger',
    ],
    AIB_COMPONENT='platform',
)

# Shim library for boost to depend on
env.Library(
    target='boost_assert_shim',
    source=[
        'util/boost_assert_shim.cpp'
    ],
    # NOTE: This library *must not* depend on any mongodb code
    LIBDEPS=[],
)

js_engine_ver = get_option("js-engine") if get_option("server-js") == "on" else "none"

# On windows, we need to escape the backslashes in the command-line
# so that windows paths look okay.
cmd_line = " ".join(sys.argv).encode('unicode_escape')

module_list = ',\n'.join(['"{0}"_sd'.format(x) for x in env['MONGO_MODULES']])

# This generates a numeric representation of the version string so that
# you can easily compare versions of MongoDB without having to parse
# the version string.
#
# The rules for this are
# {major}{minor}{release}{pre/rc/final}
# If the version is pre-release and not an rc, the final number is 0
# If the version is an RC, the final number of 1 + rc number
# If the version is pre-release between RC's, the final number is 1 + rc number
# If the version is a final release, the final number is 99
#
# Examples:
# 3.1.1-123     = 3010100
# 3.1.1-rc2     = 3010103
# 3.1.1-rc2-123 = 3010103
# 3.1.1         = 3010199
#
version_parts = [ x for x in re.match(r'^(\d+)\.(\d+)\.(\d+)-?((?:(rc)(\d+))?.*)?',
    env['MONGO_VERSION']).groups() ]
version_extra = version_parts[3] if version_parts[3] else ""
if version_parts[4] == 'rc':
    version_parts[3] = int(version_parts[5]) + -50
elif version_parts[3]:
    version_parts[2] = int(version_parts[2]) + 1
    version_parts[3] = -100
else:
    version_parts[3] = 0
version_parts = [ int(x) for x in version_parts[:4]]

# Render the MONGO_BUILDINFO_ENVIRONMENT_DATA dict into an initializer for a
# `std::vector<VersionInfoInterface::BuildInfoField>`.
def fmtBuildInfo(data):
    def fmtBool(val):
        return "true" if val else "false"
    def fmtStr(val):
        return 'R"({0})"_sd'.format(val.replace("\\", r"\\"))
    def fmtObj(obj):
        return '{{{}, {}, {}, {}}}'.format(fmtStr(obj['key']),
                                           fmtStr(env.subst(obj['value'])),
                                           fmtBool(obj['inBuildInfo']),
                                           fmtBool(obj['inVersion']))
    return ',\n'.join([fmtObj(obj) for _,obj in data.items()])

buildInfoInitializer = fmtBuildInfo(env['MONGO_BUILDINFO_ENVIRONMENT_DATA'])

generatedVersionFile = env.Substfile(
    'util/version_constants.h.in',
    SUBST_DICT=[
        ('@mongo_version@', env['MONGO_VERSION']),
        ('@mongo_version_major@', version_parts[0]),
        ('@mongo_version_minor@', version_parts[1]),
        ('@mongo_version_patch@', version_parts[2]),
        ('@mongo_version_extra@', version_parts[3]),
        ('@mongo_version_extra_str@', version_extra),
        ('@mongo_git_hash@', env['MONGO_GIT_HASH']),
        ('@buildinfo_js_engine@', js_engine_ver),
        ('@buildinfo_allocator@', env['MONGO_ALLOCATOR']),
        ('@buildinfo_modules@', module_list),
        ('@buildinfo_environment_data@', buildInfoInitializer),
    ])
env.Alias('generated-sources', generatedVersionFile)

config_header_substs = (
    ('@mongo_config_altivec_vec_vbpermq_output_index@', 'MONGO_CONFIG_ALTIVEC_VEC_VBPERMQ_OUTPUT_INDEX'),
    ('@mongo_config_debug_build@', 'MONGO_CONFIG_DEBUG_BUILD'),
    ('@mongo_config_have_ssl_set_ecdh_auto@', 'MONGO_CONFIG_HAVE_SSL_SET_ECDH_AUTO'),
    ('@mongo_config_have_ssl_ec_key_new@', 'MONGO_CONFIG_HAVE_SSL_EC_KEY_NEW'),
    ('@mongo_config_have_execinfo_backtrace@', 'MONGO_CONFIG_HAVE_EXECINFO_BACKTRACE'),
    ('@mongo_config_have_fips_mode_set@', 'MONGO_CONFIG_HAVE_FIPS_MODE_SET'),
    ('@mongo_config_have_header_unistd_h@', 'MONGO_CONFIG_HAVE_HEADER_UNISTD_H'),
    ('@mongo_config_have_memset_s@', 'MONGO_CONFIG_HAVE_MEMSET_S'),
    ('@mongo_config_have_posix_monotonic_clock@', 'MONGO_CONFIG_HAVE_POSIX_MONOTONIC_CLOCK'),
    ('@mongo_config_have_pthread_setname_np@', 'MONGO_CONFIG_HAVE_PTHREAD_SETNAME_NP'),
    ('@mongo_config_have_std_enable_if_t@', 'MONGO_CONFIG_HAVE_STD_ENABLE_IF_T'),
    ('@mongo_config_have_strnlen@', 'MONGO_CONFIG_HAVE_STRNLEN'),
    ('@mongo_config_max_extended_alignment@', 'MONGO_CONFIG_MAX_EXTENDED_ALIGNMENT'),
    ('@mongo_config_optimized_build@', 'MONGO_CONFIG_OPTIMIZED_BUILD'),
    ('@mongo_config_ssl@', 'MONGO_CONFIG_SSL'),
    ('@mongo_config_ssl_has_asn1_any_definitions@', 'MONGO_CONFIG_HAVE_ASN1_ANY_DEFINITIONS'),
    ('@mongo_config_ssl_provider@', 'MONGO_CONFIG_SSL_PROVIDER'),
    ('@mongo_config_usdt_enabled@', 'MONGO_CONFIG_USDT_ENABLED'),
    ('@mongo_config_usdt_provider@', 'MONGO_CONFIG_USDT_PROVIDER'),
    ('@mongo_config_use_libunwind@', 'MONGO_CONFIG_USE_LIBUNWIND'),
    ('@mongo_config_use_raw_latches@', 'MONGO_CONFIG_USE_RAW_LATCHES'),
    ('@mongo_config_wiredtiger_enabled@', 'MONGO_CONFIG_WIREDTIGER_ENABLED'),
)

def makeConfigHeaderDefine(self, key):
    val = "// #undef {0}".format(key)
    if key in self['CONFIG_HEADER_DEFINES']:
        val = "#define {0} {1}".format(key, self['CONFIG_HEADER_DEFINES'][key])
    return val
env.AddMethod(makeConfigHeaderDefine)

generateConfigHeaderFile = env.Substfile(
    'config.h.in',
    SUBST_DICT=[(k, env.makeConfigHeaderDefine(v)) for (k, v) in config_header_substs]
)
env.Alias('generated-sources', generateConfigHeaderFile)

env.Library(
    target="mongod_options_init",
    source=[
        "db/mongod_options_init.cpp",
    ],
    LIBDEPS=[
        'base',
    ],
    LIBDEPS_PRIVATE=[
        'db/mongod_options',
        '$BUILD_DIR/mongo/util/net/ssl_options_server' if get_option('ssl') == 'on' else '',
    ]
)

mongod = env.Program(
    target="mongod",
    source=[
        'db/db.cpp',
        'db/logical_session_cache_factory_mongod.cpp',
        'db/read_write_concern_defaults_cache_lookup_mongod.cpp',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/third_party/shim_snappy',
        'base',
        'db/auth/auth_op_observer',
        'db/auth/authmongod',
        'db/background',
        'db/bson/dotted_path_support',
        'db/catalog/catalog_impl',
        'db/catalog/collection_options',
        'db/catalog/document_validation',
        'db/catalog/health_log',
        'db/catalog/index_key_validate',
        'db/client_metadata_propagation_egress_hook',
        'db/collection_index_usage_tracker',
        'db/commands/mongod_fcv',
        'db/commands/mongod',
        'db/commands/server_status_servers',
        'db/common',
        'db/concurrency/flow_control_ticketholder',
        'db/concurrency/lock_manager',
        'db/concurrency/write_conflict_exception',
        'db/curop_metrics',
        'db/curop',
        'db/db_raii',
        'db/dbdirectclient',
        'db/dbhelpers',
        'db/exec/working_set',
        'db/free_mon/free_mon_mongod',
        'db/ftdc/ftdc_mongod',
        'db/fts/ftsmongod',
        'db/index_builds_coordinator_mongod',
        'db/index/index_access_method',
        'db/index/index_access_methods',
        'db/index/index_descriptor',
        'db/initialize_server_security_state',
        'db/initialize_snmp',
        'db/introspect',
        'db/keys_collection_client_direct',
        'db/kill_sessions_local',
        'db/logical_session_cache_impl',
        'db/logical_time_metadata_hook',
        'db/matcher/expressions_mongod_only',
        'db/mirror_maestro',
        'db/mongod_options',
        'db/ops/write_ops_parsers',
        'db/periodic_runner_job_abort_expired_transactions',
        'db/periodic_runner_job_decrease_snapshot_cache_pressure',
        'db/pipeline/aggregation',
        'db/pipeline/process_interface/mongod_process_interface_factory',
        'db/query_exec',
        'db/read_concern_d_impl',
        'db/read_write_concern_defaults',
        'db/repair_database_and_check_version',
        'db/repl/bgsync',
        'db/repl/oplog_application',
        'db/repl/oplog_buffer_blocking_queue',
        'db/repl/oplog_buffer_collection',
        'db/repl/oplog_buffer_proxy',
        'db/repl/repl_coordinator_impl',
        'db/repl/repl_set_commands',
        'db/repl/repl_settings',
        'db/repl/rs_rollback',
        'db/repl/serveronly_repl',
        'db/repl/storage_interface_impl',
        'db/repl/topology_coordinator',
        'db/rw_concern_d',
        'db/s/balancer',
        'db/s/op_observer_sharding_impl',
        'db/s/sessions_collection_config_server',
        'db/s/sharding_commands_d',
        'db/s/sharding_runtime_d',
        'db/service_context_d',
        'db/service_liaison_mongod',
        'db/sessions_collection_rs',
        'db/sessions_collection_standalone',
        'db/startup_warnings_mongod',
        'db/stats/counters',
        'db/stats/serveronly_stats',
        'db/stats/top',
        'db/storage/backup_cursor_hooks',
        'db/storage/biggie/storage_biggie',
        'db/storage/devnull/storage_devnull',
        'db/storage/ephemeral_for_test/storage_ephemeral_for_test',
        'db/storage/flow_control_parameters',
        'db/storage/flow_control',
        'db/storage/storage_engine_lock_file',
        'db/storage/storage_engine_metadata',
        'db/storage/storage_init_d',
        'db/storage/storage_options',
        'db/storage/wiredtiger/storage_wiredtiger' if wiredtiger else [],
        'db/system_index',
        'db/traffic_recorder',
        'db/ttl_collection_cache',
        'db/ttl_d',
        'db/update_index_data',
        'db/update/update_driver',
        'db/views/views_mongod',
        'executor/network_interface_factory',
        'mongod_options_init',
        'rpc/rpc',
        's/commands/shared_cluster_commands',
        's/sessions_collection_sharded',
        'scripting/scripting_server',
        'transport/message_compressor_options_server',
        'transport/service_entry_point',
        'transport/transport_layer_manager',
        'util/clock_sources',
        'util/elapsed_tracker',
        'util/fail_point',
        'util/latch_analyzer' if get_option('use-diagnostic-latches') == 'on' else [],
        'util/net/network',
        'util/ntservice',
        'util/options_parser/options_parser_init',
        'util/periodic_runner_factory',
        'util/version_impl',
        'watchdog/watchdog_mongod',
    ],
    AIB_COMPONENT="mongod",
    AIB_COMPONENTS_EXTRA=[
        "core",
        "default",
        "dist",
        "dist-test",
        "servers",
        "integration-tests",
    ],
)

hygienic = get_option('install-mode') == 'hygienic'

if not hygienic:
    env.Default(env.Install('#/', mongod))

mongotrafficreader = env.Program(
    target="mongotrafficreader",
    source=[
        "db/traffic_reader_main.cpp"
    ],
    LIBDEPS=[
        'base',
        'db/traffic_reader',
        'rpc/protocol',
        'util/signal_handlers'
    ],
)

if not hygienic:
    env.Install('#/', mongotrafficreader)

# mongos
mongos = env.Program(
    target='mongos',
    source=[
        "db/read_write_concern_defaults_cache_lookup_mongos.cpp",
        's/cluster_cursor_stats.cpp',
        's/mongos_options.cpp',
        's/mongos_options_init.cpp',
        env.Idlc('s/mongos_options.idl')[0],
        's/router_transactions_server_status.cpp',
        's/s_sharding_server_status.cpp',
        's/server.cpp',
        's/service_entry_point_mongos.cpp',
        's/sharding_uptime_reporter.cpp',
        's/version_mongos.cpp',
    ],
    LIBDEPS=[
        'db/audit',
        'db/auth/authmongos',
        'db/commands/server_status',
        'db/commands/server_status_core',
        'db/commands/server_status_servers',
        'db/curop',
        'db/dbdirectclient',
        'db/ftdc/ftdc_mongos',
        'db/initialize_server_security_state',
        'db/logical_session_cache',
        'db/logical_session_cache_impl',
        'db/logical_time_metadata_hook',
        'db/read_write_concern_defaults',
        'db/server_options',
        'db/server_options_base',
        'db/service_liaison_mongos',
        'db/session_catalog',
        'db/startup_warnings_common',
        'db/stats/counters',
        's/commands/cluster_commands',
        's/commands/shared_cluster_commands',
        's/committed_optime_metadata_hook',
        's/coreshard',
        's/is_mongos',
        's/query/cluster_cursor_cleanup_job',
        's/sessions_collection_sharded',
        's/sharding_egress_metadata_hook_for_mongos',
        's/sharding_initialization',
        's/sharding_router_api',
        'transport/message_compressor_options_server',
        'transport/service_entry_point',
        'transport/transport_layer_manager',
        'util/clock_sources',
        'util/fail_point',
        'util/latch_analyzer' if get_option('use-diagnostic-latches') == 'on' else [],
        'util/net/ssl_options_server' if get_option('ssl') == 'on' else '',
        'util/ntservice',
        'util/version_impl',
    ],
    LIBDEPS_PRIVATE=[
        'util/options_parser/options_parser_init',
        'util/options_parser/options_parser',
    ],
    AIB_COMPONENT="mongos",
    AIB_COMPONENTS_EXTRA=[
        "core",
        "dist",
        "dist-test",
        "servers",
        "integration-tests",
    ]
)

if not hygienic:
    env.Install('#/', mongos)

env.Library("linenoise_utf8",
    source=[
        "shell/linenoise_utf8.cpp",
    ])

# --- shell ---

if not has_option('noshell') and usemozjs:
    shell_core_env = env.Clone()
    if has_option("safeshell"):
        shell_core_env.Append(CPPDEFINES=["MONGO_SAFE_SHELL"])
    shell_core_env.Library("shell_core",
                source=[
                    "shell/linenoise.cpp",
                    "shell/mk_wcwidth.cpp"
                ],
                LIBDEPS=[
                    'client/clientdriver_network',
                    'db/catalog/index_key_validate',
                    'db/logical_session_id_helpers',
                    'db/mongohasher',
                    'db/query/command_request_response',
                    'db/query/query_request',
                    'db/server_options_core',
                    'db/traffic_reader',
                    'linenoise_utf8',
                    'rpc/protocol',
                    'scripting/scripting',
                    'shell/benchrun',
                    'shell/mongojs',
                    'shell/shell_utils',
                    'transport/message_compressor',
                    'transport/transport_layer_manager',
                    'util/net/network',
                    'util/options_parser/options_parser_init',
                    'util/password',
                    'util/processinfo',
                    'util/signal_handlers',
                    'util/version_impl',
                    'executor/thread_pool_task_executor',
                    'executor/network_interface_thread_pool',
                    'executor/network_interface_factory'
                ],
    )

    shellEnv = env.Clone()
    
    mongo_shell = shellEnv.Program(
        "mongo",
        [
            "shell/dbshell.cpp",
            "shell/mongodbcr.cpp",
            "shell/shell_options_init.cpp",
        ],
        LIBDEPS=[
            "$BUILD_DIR/third_party/shim_pcrecpp",
            "shell_core",
            "db/server_options_core",
            "client/clientdriver_network",
            "shell/kms_shell" if get_option('ssl') == 'on' else '',
            "shell/encrypted_dbclient" if get_option('ssl') == 'on' else '',
            "$BUILD_DIR/mongo/util/password",
            '$BUILD_DIR/mongo/db/storage/duplicate_key_error_info',
            "$BUILD_DIR/mongo/db/views/resolved_view",
        ],
        LIBDEPS_PRIVATE=[
            'shell/shell_options_register',
            'transport/message_compressor_options_client',
            "$BUILD_DIR/mongo/client/connection_string",
            '$BUILD_DIR/mongo/util/net/ssl_options_client' if get_option('ssl') == 'on' else '',
        ],
        AIB_COMPONENT="mongo",
        AIB_COMPONENTS_EXTRA=[
            "core",
            "dist",
            "dist-test",
            "shell",
            "integration-tests",
        ],
    )

    if not hygienic:
        shellEnv.Install( '#/', mongo_shell )
else:
    shellEnv = None

#  ----  INSTALL -------

# binaries

distBinaries = []
distDebugSymbols = []

def add_exe( v ):
    return "${PROGPREFIX}%s${PROGSUFFIX}" % v

def failMissingObjCopy(env, target, source):
    env.FatalError("Generating debug symbols requires objcopy, please set the OBJCOPY variable.")

def installBinary( e, name ):

    if hygienic:
        return

    debug_sym_name = name
    name = add_exe( name )

    debug_sym_cmd = None

    if 'OBJCOPY' not in e:
        debug_sym_cmd = failMissingObjCopy
    else:
        debug_sym_cmd = '${OBJCOPY} --only-keep-debug ${SOURCE} ${TARGET}'
    debug_sym_name += '.debug'

    if debug_sym_cmd:
        debug_sym = e.Command(
            debug_sym_name,
            name,
            debug_sym_cmd
        )
        e.NoCache(debug_sym)
        e.Install("#/", debug_sym)
        e.Alias('debugsymbols', debug_sym)
        distDebugSymbols.append(debug_sym)

    if not has_option("nostrip"):
        stripped_name = 'stripped/%s' % name
        strip_cmd = e.Command(
            stripped_name,
            [name, debug_sym],
            '${OBJCOPY} --strip-debug --add-gnu-debuglink ${SOURCES[1]} ${SOURCES[0]} $TARGET'
        )
        e.NoCache(stripped_name)
        distBinaries.append(stripped_name)
    else:
        distBinaries.append(name)

    inst = e.Install( "$DESTDIR/bin", name )

    e.AddPostAction( inst, 'chmod 755 $TARGET' )

# legacy tools
if not hygienic:
    env.Alias("tools", "#/" + add_exe("mongobridge"))

installBinary( env, "mongod" )
installBinary( env, "mongos" )

if shellEnv is not None:
    installBinary( shellEnv, "mongo" )
    if not hygienic:
        env.Alias( "core", [ '#/%s' % b for b in [ add_exe( "mongo" ) ] ] )

if not hygienic:
    env.Alias( "core", [ '#/%s' % b for b in [ add_exe( "mongod" ), add_exe( "mongos" ) ] ] )

# Stage the top-level mongodb banners
distsrc = env.Dir('#distsrc')
if hygienic:
    env.AutoInstall(
        target='$PREFIX',
        source=[
            distsrc.File('README'),
            # TODO: we need figure out what to do when we use a different
            # THIRD-PARTY-NOTICES for example, with Embedded
            distsrc.File('THIRD-PARTY-NOTICES'),
            distsrc.File('MPL-2'),
        ],
        AIB_COMPONENT='common',
        AIB_ROLE='base',
    )
else:
    env.Append(MODULE_BANNERS = [distsrc.File('README'),
                                 distsrc.File('THIRD-PARTY-NOTICES'),
                                 distsrc.File('MPL-2')])

# If no module has introduced a file named LICENSE-Enterprise.txt then this
# is a Community build, so inject the AGPL and the Community license

enterprise_license = [banner for banner in env["MODULE_BANNERS"] if banner.name ==  "LICENSE-Enterprise.txt"]
if not enterprise_license:
    env.Append(MODULE_BANNERS = [distsrc.File('LICENSE-Community.txt')])

# All module banners get staged to the top level of the tarfile, so we
# need to fail if we are going to have a name collision.
module_banner_filenames = set([f.name for f in env['MODULE_BANNERS']])
if not len(module_banner_filenames) == len(env['MODULE_BANNERS']):
    # TODO: Be nice and identify conflicts in error.
    env.FatalError("ERROR: Filename conflicts exist in module banners.")

if hygienic:
    env.AutoInstall(
        target='$PREFIX',
        source=env.get('MODULE_BANNERS', []),
        AIB_COMPONENT='common',
        AIB_COMPONENTS_EXTRA=['dist', 'dist-test'],
        AIB_ROLE='base',
    )

# Build a set of directories containing module banners, and use that
# to build a --transform option for each directory so that the files
# are tar'ed up to the proper location.
module_banner_dirs = set([Dir('#').rel_path(f.get_dir()) for f in env['MODULE_BANNERS']])
module_banner_transforms = ["--transform %s=$SERVER_DIST_BASENAME" % d for d in module_banner_dirs]

# Allow modules to map original file name directories to subdirectories
# within the archive (e.g. { "src/mongo/db/modules/enterprise/docs": "snmp"})
archive_addition_transforms = []
for full_dir, archive_dir in list(env["ARCHIVE_ADDITION_DIR_MAP"].items()):
  archive_addition_transforms.append("--transform \"%s=$SERVER_DIST_BASENAME/%s\"" %
                                     (full_dir, archive_dir))

for target in env["DIST_BINARIES"]:
    installBinary(env, "db/modules/" + target)

# Set the download url to the right place
compass_type = 'compass-community'
if 'enterprise' in env['MONGO_MODULES']:
    compass_type = 'compass'

compass_script = "install_compass.in"

compass_python_interpreter = '/usr/bin/env python2'

compass_installer = env.Substfile(
  target="$BUILD_DIR/mongo/installer/compass/" + compass_script[:-3],
  source='installer/compass/' + compass_script,
  SUBST_DICT=[
    ('@compass_type@', compass_type),
    ('@python_interpreter@', compass_python_interpreter),
  ],
)

distBinaries.append(compass_installer)

if not hygienic:
    compass_script_installer = env.Install("$DESTDIR/bin", compass_installer)
else:
    compass_script_installer = env.AutoInstall(
        target='$PREFIX_BINDIR',
        source=[
            compass_installer,
        ],
        AIB_COMPONENT='dist',
        AIB_ROLE='runtime',
    )

env.AddPostAction( compass_script_installer, 'chmod 755 $TARGET' )
env.AddPostAction( compass_installer, 'chmod 755 $TARGET' )

if not hygienic:
    server_archive = env.Command(
        target='#/${SERVER_ARCHIVE}',
        source=['#buildscripts/make_archive.py'] + env["MODULE_BANNERS"] + env["ARCHIVE_ADDITIONS"] + distBinaries,
        action=' '.join(
            ['$PYTHON ${SOURCES[0]} -o $TARGET'] +
            archive_addition_transforms +
            module_banner_transforms +
            [
                '--transform $BUILD_DIR/mongo/db/modules/enterprise=$SERVER_DIST_BASENAME/bin',
                '--transform $BUILD_DIR/mongo/stripped/db/modules/enterprise=$SERVER_DIST_BASENAME/bin',
                '--transform $BUILD_DIR/mongo/stripped=$SERVER_DIST_BASENAME/bin',
                '--transform $BUILD_DIR/mongo=$SERVER_DIST_BASENAME/bin',
                '--transform src/mongo/installer/compass=$SERVER_DIST_BASENAME/bin',
                '${TEMPFILE(SOURCES[1:])}'
            ],
        ),
        BUILD_DIR=env.Dir('$BUILD_DIR').path
    )

    env.Alias("dist", server_archive)
    env.NoCache(server_archive)

    debug_symbols_dist = env.Command(
        target='#/${SERVER_DIST_BASENAME}-debugsymbols${DIST_ARCHIVE_SUFFIX}',
        source=['#buildscripts/make_archive.py'] + distDebugSymbols,
        action=' '.join(
            [
                '$PYTHON ${SOURCES[0]} -o $TARGET',
                '--transform $BUILD_DIR/mongo/db/modules/enterprise=$SERVER_DIST_BASENAME',
                '--transform $BUILD_DIR/mongo=$SERVER_DIST_BASENAME',
                '${TEMPFILE(SOURCES[1:])}',
            ]
        ),
        BUILD_DIR=env.Dir('$BUILD_DIR').path
    )

    env.Alias('dist-debugsymbols', debug_symbols_dist)
    env.NoCache(debug_symbols_dist)

#final alias
if not hygienic:
    env.Alias( "install", "$DESTDIR" )
