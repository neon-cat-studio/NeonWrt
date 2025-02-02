# -*- mode: python; -*-

# This SConscript describes build rules for the "mongo" project.

import itertools
import os
import re
import subprocess
import sys
from buildscripts import utils

Import("env")
Import("has_option")
Import("get_option")
Import("usev8")
Import("v8suffix")
Import("wiredtiger")

# Boost we need everywhere. 's2' is spammed in all over the place by
# db/geo unfortunately. pcre is also used many places.
env.InjectThirdPartyIncludePaths(libraries=['boost', 's2', 'pcre'])
env.InjectMongoIncludePaths()

env.SConscript(['base/SConscript',
                'crypto/SConscript',
                'crypto/tom/SConscript',
                'db/auth/SConscript',
                'db/catalog/SConscript',
                'db/commands/SConscript',
                'db/concurrency/SConscript',
                'db/geo/SConscript',
                'db/exec/SConscript',
                'db/fts/SConscript',
                'db/index/SConscript',
                'db/ops/SConscript',
                'db/query/SConscript',
                'db/repl/SConscript',
                'db/sorter/SConscript',
                'db/storage/SConscript',
                'db/storage/devnull/SConscript',
                'db/storage/in_memory/SConscript',
                'db/storage/kv/SConscript',
                'db/storage/mmap_v1/SConscript',
                'db/storage/rocks/SConscript',
                'db/storage/wiredtiger/SConscript',
                'db/SConscript',
                'logger/SConscript',
                'platform/SConscript',
                's/SConscript',
                'unittest/SConscript',
                'util/concurrency/SConscript',
                'util/options_parser/SConscript',
                'util/cmdline_utils/SConscript',
                'util/mongoutils/SConscript'])

def add_exe( v ):
    return "${PROGPREFIX}%s${PROGSUFFIX}" % v

# ------    SOURCE FILE SETUP -----------

env.Library('foundation',
            [ 'util/assert_util.cpp',
              'util/concurrency/mutex.cpp',
              'util/concurrency/thread_pool.cpp',
              'util/debugger.cpp',
              'util/exception_filter_win32.cpp',
              'util/file.cpp',
              'util/log.cpp',
              'util/platform_init.cpp',
              'util/text.cpp',
              'util/time_support.cpp',
              'util/timer.cpp',
              'util/thread_safe_string.cpp',
              "util/touch_pages.cpp",
              "util/startup_test.cpp",
              ],
            LIBDEPS=['stacktrace',
                     'synchronization',
                     '$BUILD_DIR/mongo/base/base',
                     '$BUILD_DIR/mongo/logger/logger',
                     '$BUILD_DIR/mongo/platform/platform',
                     '$BUILD_DIR/mongo/util/concurrency/thread_name',
                     '$BUILD_DIR/third_party/shim_allocator',
                     '$BUILD_DIR/third_party/shim_boost',
                     '$BUILD_DIR/third_party/shim_tz'])

env.CppUnitTest('text_test', 'util/text_test.cpp', LIBDEPS=['foundation'])
env.CppUnitTest('util/time_support_test', 'util/time_support_test.cpp', LIBDEPS=['foundation'])

env.Library('stringutils', ['util/stringutils.cpp', 'util/base64.cpp', 'util/hex.cpp'])

env.Library('md5', [
        'util/md5.cpp',
        'util/password_digest.cpp',
        ])

env.CppUnitTest( "md5_test", ["util/md5_test.cpp", "util/md5main.cpp" ],
                 LIBDEPS=["md5"] )

env.CppUnitTest( "stringutils_test", [ "util/stringutils_test.cpp" ],
                 LIBDEPS=["stringutils"] )

env.Library('bson', [
        'bson/mutable/document.cpp',
        'bson/mutable/element.cpp',
        'bson/util/bson_extract.cpp',
        'util/safe_num.cpp',
        'bson/bson_validate.cpp',
        'bson/oid.cpp',
        "bson/optime.cpp",
        'bson/bson_startuptest.cpp',
        'bson/bsonelement.cpp',
        'bson/bsonmisc.cpp',
        'bson/bsonobj.cpp',
        'bson/bsonobjbuilder.cpp',
        'bson/bsonobjiterator.cpp',
        'bson/bsontypes.cpp',
        'db/json.cpp'
        ], LIBDEPS=[
        'base/base',
        'md5',
        'stringutils',
        '$BUILD_DIR/mongo/platform/platform',
        ])

env.Library('mutable_bson_test_utils', [
        'bson/mutable/mutable_bson_test_utils.cpp'
        ], LIBDEPS=['bson'])

env.CppUnitTest('builder_test', ['bson/util/builder_test.cpp'],
                LIBDEPS=['bson'])

env.CppUnitTest('mutable_bson_test', ['bson/mutable/mutable_bson_test.cpp'],
                 LIBDEPS=['bson', 'mutable_bson_test_utils'])

env.CppUnitTest('mutable_bson_algo_test', ['bson/mutable/mutable_bson_algo_test.cpp'],
                LIBDEPS=['bson', 'mutable_bson_test_utils'])

env.CppUnitTest('safe_num_test', ['util/safe_num_test.cpp'],
                LIBDEPS=['bson'])

env.CppUnitTest('string_map_test', ['util/string_map_test.cpp'],
                LIBDEPS=['bson','foundation'])

env.CppUnitTest('bson_field_test', ['bson/bson_field_test.cpp'],
                LIBDEPS=['bson'])

env.CppUnitTest('bson_obj_test', ['bson/bson_obj_test.cpp'],
                LIBDEPS=['bson'])

env.CppUnitTest('bson_validate_test', ['bson/bson_validate_test.cpp'],
                LIBDEPS=['bson'])

env.CppUnitTest('bsonobjbuilder_test', ['bson/bsonobjbuilder_test.cpp'],
                LIBDEPS=['bson'])

env.CppUnitTest('namespace_string_test', ['db/namespace_string_test.cpp'],
                LIBDEPS=['namespace_string'])

env.CppUnitTest('update_index_data_test', ['db/update_index_data_test.cpp'],
                LIBDEPS=['bson','update_index_data','db/common'])

env.CppUnitTest('oid_test', ['bson/oid_test.cpp'],
                LIBDEPS=['bson'])

env.Library('path',
            ['db/matcher/path.cpp',
             'db/matcher/path_internal.cpp'],
            LIBDEPS=['bson',
                     '$BUILD_DIR/mongo/db/common'])

env.CppUnitTest('path_test', ['db/matcher/path_test.cpp'],
                LIBDEPS=['path'])


env.Library('expressions',
            ['db/matcher/expression.cpp',
             'db/matcher/expression_array.cpp',
             'db/matcher/expression_leaf.cpp',
             'db/matcher/expression_tree.cpp',
             'db/matcher/expression_parser.cpp',
             'db/matcher/expression_parser_tree.cpp',
             'db/matcher/expression_where_noop.cpp',
             'db/matcher/matchable.cpp',
             'db/matcher/match_details.cpp'],
            LIBDEPS=['bson',
                     'path',
                     '$BUILD_DIR/mongo/db/common',
                     '$BUILD_DIR/third_party/shim_pcrecpp'
                     ] )

env.Library('expressions_geo',
            ['db/matcher/expression_geo.cpp',
             'db/matcher/expression_parser_geo.cpp'],
            LIBDEPS=['expressions','db/geo/geometry','db/geo/geoparser'] )

env.Library('expressions_text',
            ['db/matcher/expression_text.cpp',
             'db/matcher/expression_parser_text.cpp'],
            LIBDEPS=['expressions','db/fts/base'] )

env.CppUnitTest('expression_test',
                ['db/matcher/expression_test.cpp',
                 'db/matcher/expression_leaf_test.cpp',
                 'db/matcher/expression_tree_test.cpp',
                 'db/matcher/expression_array_test.cpp'],
                LIBDEPS=['expressions'] )

env.CppUnitTest('expression_geo_test',
                ['db/matcher/expression_geo_test.cpp',
                 'db/matcher/expression_parser_geo_test.cpp'],
                LIBDEPS=['expressions_geo'] )

env.CppUnitTest('expression_text_test',
                ['db/matcher/expression_parser_text_test.cpp'],
                LIBDEPS=['expressions_text'] )

env.CppUnitTest('expression_parser_test',
                ['db/matcher/expression_parser_test.cpp',
                 'db/matcher/expression_parser_array_test.cpp',
                 'db/matcher/expression_parser_tree_test.cpp',
                 'db/matcher/expression_parser_leaf_test.cpp'],
                LIBDEPS=['expressions'] )


env.CppUnitTest('bson_extract_test', ['bson/util/bson_extract_test.cpp'], LIBDEPS=['bson'])
env.CppUnitTest('bson_check_test', ['bson/util/bson_check_test.cpp'], LIBDEPS=['bson'])

env.CppUnitTest('descriptive_stats_test',
                ['util/descriptive_stats_test.cpp'],
                LIBDEPS=['foundation', 'bson']);

env.CppUnitTest('sock_test', ['util/net/sock_test.cpp'],
                LIBDEPS=['network',
                         'synchronization',
                ])

env.CppUnitTest('curop_test',
                ['db/curop_test.cpp'],
                LIBDEPS=['serveronly', 'coredb', 'coreserver', 'ntservice_mock'],
                NO_CRUTCH=True)

env.Library('index_names',["db/index_names.cpp"])

env.Library( 'mongohasher', [ "db/hasher.cpp" ] )

env.Library('synchronization', [ 'util/concurrency/synchronization.cpp' ])

env.Library('auth_helpers', ['client/auth_helpers.cpp'],
            LIBDEPS=['clientdriver'])

env.Library('global_optime', ['db/global_optime.cpp'])

env.Library('spin_lock', ["util/concurrency/spin_lock.cpp"])
env.CppUnitTest('spin_lock_test', ['util/concurrency/spin_lock_test.cpp'],
                LIBDEPS=['spin_lock', '$BUILD_DIR/third_party/shim_boost'])

env.Library('hostandport', ['util/net/hostandport.cpp'],
            LIBDEPS=[
                'foundation',
                'server_options_core',
            ])

env.CppUnitTest('hostandport_test', ['util/net/hostandport_test.cpp'],
                LIBDEPS=['hostandport'])

env.Library('network', [
            "util/net/sock.cpp",
            "util/net/socket_poll.cpp",
            "util/net/ssl_expiration.cpp",
            "util/net/ssl_manager.cpp",
            "util/net/ssl_options.cpp",
            "util/net/httpclient.cpp",
            "util/net/message.cpp",
            "util/net/message_port.cpp",
            "util/net/listen.cpp" ],
            LIBDEPS=['$BUILD_DIR/mongo/util/concurrency/ticketholder',
                     '$BUILD_DIR/mongo/util/options_parser/options_parser',
                     'background_job',
                     'fail_point',
                     'foundation',
                     'hostandport',
                     'server_options_core',
            ])

env.Library(
    target='index_key_validate',
    source=[
        "db/catalog/index_key_validate.cpp",
    ],
    LIBDEPS=[
        'bson',
        'db/common',
        'index_names',
    ])

js_engine = "V8" if usev8 else "Unknown"

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
    version_parts[3] = -100
else:
    version_parts[3] = 0
version_parts = [ int(x) for x in version_parts[:4]]

sysInfo = " ".join(os.uname())
gitVersion = env['MONGO_GIT_HASH']
if len(env['MONGO_MODULES']) > 0:
    gitVersion += " modules: " + ", ".join(env['MONGO_MODULES'])

versionInfo = env.Substfile(
    'util/version.cpp.in',
    SUBST_DICT=[
        ('@mongo_version@', env['MONGO_VERSION']),
        ('@mongo_version_major@', version_parts[0]),
        ('@mongo_version_minor@', version_parts[1]),
        ('@mongo_version_patch@', version_parts[2]),
        ('@mongo_version_extra@', version_parts[3]),
        ('@mongo_version_extra_str@', version_extra),
        ('@mongo_git_version@', gitVersion),
        ('@buildinfo_js_engine@', js_engine),
        ('@buildinfo_allocator@', GetOption('allocator')),
        ('@buildinfo_loader_flags@', env.subst("$LINKGFLAGS $LDFLAGS")),
        ('@buildinfo_compiler_flags@', env.subst("$CXXFLAGS $CCFLAGS $CFLAGS")),
        ('@buildinfo_sysinfo@', sysInfo),
    ])

env.Library('clientdriver', [
            "client/connpool.cpp",
            "client/dbclient.cpp",
            "client/dbclient_rs.cpp",
            "client/dbclientcursor.cpp",
            'client/native_sasl_client_session.cpp',
            "client/replica_set_monitor.cpp",
            'client/sasl_client_authenticate.cpp',
            "client/sasl_client_authenticate_impl.cpp",
            'client/sasl_client_conversation.cpp',
            'client/sasl_client_session.cpp',
            'client/sasl_plain_client_conversation.cpp',
            'client/sasl_scramsha1_client_conversation.cpp',
            "client/syncclusterconnection.cpp",
            "db/dbmessage.cpp"
            ],
            LIBDEPS=['$BUILD_DIR/mongo/db/auth/authcommon',
                     '$BUILD_DIR/mongo/crypto/scramauth',
                     'network'
            ])

env.CppUnitTest("replica_set_monitor_test",
                ["client/replica_set_monitor_test.cpp"],
                LIBDEPS=["clientdriver"])

env.Library('lasterror', [
            "db/lasterror.cpp",
            ],
            LIBDEPS=['network',
                     'foundation',
            ])

env.Library('version',
            [
                'util/version.cpp'
            ],
            LIBDEPS=[
                'bson',
                '$BUILD_DIR/mongo/base/base'
            ])

env.Library('namespace_string', ['db/namespace_string.cpp'], LIBDEPS=['foundation'])

commonFiles = [ "shell/mongo.cpp",
                "util/intrusive_counter.cpp",
                "util/file_allocator.cpp",
                "util/paths.cpp",
                "util/progress_meter.cpp",
                "util/concurrency/task.cpp",
                "util/password.cpp",
                "util/concurrency/rwlockimpl.cpp",
                "util/text_startuptest.cpp",
                'util/signal_win32.cpp',
                ]

extraCommonLibdeps = []

if env['MONGO_BUILD_SASL_CLIENT']:
    saslLibs = ['sasl2']

    env.Library('cyrus_sasl_client_session',
                ['client/cyrus_sasl_client_session.cpp',
                 'client/sasl_sspi.cpp'],
                LIBDEPS = [
                    'clientdriver',
                    'foundation',
                    'signal_handlers_synchronous',
                ],
                SYSLIBDEPS=saslLibs)
    extraCommonLibdeps.append('cyrus_sasl_client_session')

# handle processinfo*
processInfoFiles = [ "util/processinfo.cpp" ]

processInfoPlatformFile = env.File( "util/processinfo_${PYSYSPLATFORM}.cpp" )
# NOTE( schwerin ): This is a very un-scons-y way to make this decision, and prevents one from using
# code generation to produce util/processinfo_$PYSYSPLATFORM.cpp.
if not os.path.exists( str( processInfoPlatformFile ) ):
    processInfoPlatformFile = env.File( "util/processinfo_none.cpp" )

processInfoFiles.append( processInfoPlatformFile )

env.Library("processinfo",
            processInfoFiles,
            LIBDEPS=["foundation", "bson"])

env.CppUnitTest("processinfo_test",
                ["util/processinfo_test.cpp"],
                LIBDEPS=["processinfo"])

env.Library("server_parameters",
            ["db/server_parameters.cpp"],
            LIBDEPS=["foundation","bson"])

env.CppUnitTest("server_parameters_test",
                [ "db/server_parameters_test.cpp" ],
                LIBDEPS=["server_parameters"] )


env.Library("fail_point",
            ["util/fail_point.cpp",
             "util/fail_point_registry.cpp",
             "util/fail_point_service.cpp"],
            LIBDEPS=["foundation", "bson"])

env.Library('mongocommon', commonFiles,
            LIBDEPS=['auth_helpers',
                     'bson',
                     'background_job',
                     'clientdriver',
                     'fail_point',
                     'foundation',
                     'global_environment_experiment',
                     'lasterror',
                     'md5',
                     'mongohasher',
                     'namespace_string',
                     'network',
                     'processinfo',
                     'spin_lock',
                     'stacktrace',
                     'stringutils',
                     'synchronization',
                     'util/concurrency/thread_name',
                     'version',
                     '$BUILD_DIR/third_party/shim_pcrecpp',
                     '$BUILD_DIR/third_party/murmurhash3/murmurhash3',
                     '$BUILD_DIR/third_party/shim_boost',
                     '$BUILD_DIR/mongo/util/options_parser/options_parser',
                     ] +
                     extraCommonLibdeps)

env.Library('background_job', ["util/background.cpp"],
            LIBDEPS=['spin_lock'])

env.CppUnitTest(
    target="background_job_test",
    source=[
        "util/background_job_test.cpp",
    ],
    LIBDEPS=[
        "background_job",
        "network", # Temporary crutch since the ssl cleanup is hard coded in background.cpp
        "synchronization",
    ]
)

if get_option('allocator') == 'tcmalloc':
    tcmspEnv = env.Clone()

    # Add in the include path for our vendored tcmalloc.
    tcmspEnv.InjectThirdPartyIncludePaths('gperftools')

    # If our changes to tcmalloc are ever upstreamed, this should become set based on a top
    # level configure check, though its effects should still be scoped just to these files.
    tcmspEnv.Append(
        CPPDEFINES=['MONGO_HAVE_GPERFTOOLS_GET_THREAD_CACHE_SIZE']
    )

    tcmspEnv.Library('tcmalloc_set_parameter',
                [
                    'util/tcmalloc_server_status_section.cpp',
                    'util/tcmalloc_set_parameter.cpp',
                ],
                LIBDEPS=['server_parameters'],
                LIBDEPS_DEPENDENTS=['mongod', 'mongos'])

coredbEnv = env.Clone()
coredbEnv.InjectThirdPartyIncludePaths(libraries=['snappy'])
coredbEnv.Library("coredb", [
        "client/parallel.cpp",
        "db/audit.cpp",
        "db/commands.cpp",
        "db/commands/authentication_commands.cpp",
        "db/commands/connection_status.cpp",
        "db/commands/copydb_common.cpp",
        "db/commands/fail_point_cmd.cpp",
        "db/commands/find_and_modify_common.cpp",
        "db/commands/hashcmd.cpp",
        "db/commands/isself.cpp",
        "db/repl/isself.cpp",
        "db/commands/mr_common.cpp",
        "db/commands/list_collections_common.cpp",
        "db/commands/rename_collection_common.cpp",
        "db/commands/server_status.cpp",
        "db/commands/parameters.cpp",
        "db/commands/user_management_commands.cpp",
        "db/commands/write_commands/write_commands_common.cpp",
        "db/pipeline/pipeline.cpp",
        "db/dbcommands_generic.cpp",
        "db/matcher/matcher.cpp",
        "db/pipeline/accumulator_add_to_set.cpp",
        "db/pipeline/accumulator_avg.cpp",
        "db/pipeline/accumulator_first.cpp",
        "db/pipeline/accumulator_last.cpp",
        "db/pipeline/accumulator_min_max.cpp",
        "db/pipeline/accumulator_push.cpp",
        "db/pipeline/accumulator_sum.cpp",
        "db/pipeline/dependencies.cpp",
        "db/pipeline/document.cpp",
        "db/pipeline/document_source.cpp",
        "db/pipeline/document_source_bson_array.cpp",
        "db/pipeline/document_source_command_shards.cpp",
        "db/pipeline/document_source_geo_near.cpp",
        "db/pipeline/document_source_group.cpp",
        "db/pipeline/document_source_limit.cpp",
        "db/pipeline/document_source_match.cpp",
        "db/pipeline/document_source_merge_cursors.cpp",
        "db/pipeline/document_source_out.cpp",
        "db/pipeline/document_source_project.cpp",
        "db/pipeline/document_source_redact.cpp",
        "db/pipeline/document_source_skip.cpp",
        "db/pipeline/document_source_sort.cpp",
        "db/pipeline/document_source_unwind.cpp",
        "db/pipeline/expression.cpp",
        "db/pipeline/field_path.cpp",
        "db/pipeline/value.cpp",
        "db/projection.cpp",
        "db/stats/timer_stats.cpp",
        "s/shardconnection.cpp",
        ],
                  LIBDEPS=['db/auth/serverauth',
                           'db/commands/server_status_core',
                           'db/common',
                           'scripting_common',
                           'server_parameters',
                           'expressions',
                           'expressions_geo',
                           'expressions_text',
                           'index_names',
                           'db/exec/working_set',
                           'db/index/key_generator',
                           'db/startup_warnings_common',
                           '$BUILD_DIR/mongo/foundation',
                           '$BUILD_DIR/third_party/shim_snappy',
                           'server_options',
                           '$BUILD_DIR/mongo/util/cmdline_utils/cmdline_utils',
                           '$BUILD_DIR/mongo/logger/parse_log_component_settings',
                           'clientdriver',
                           ])

env.Library('ntservice', ['util/ntservice.cpp'],
            LIBDEPS=['foundation',
                     '$BUILD_DIR/mongo/util/options_parser/options_parser'])

env.Library('ntservice_mock', ['util/ntservice_mock.cpp'])

env.Library(
    target='scripting_common',
    source=[
        'scripting/engine.cpp',
        'scripting/utils.cpp',
    ],
)

env.Library('bson_template_evaluator', ["scripting/bson_template_evaluator.cpp"],
            LIBDEPS=['bson'])
env.CppUnitTest('bson_template_evaluator_test', ['scripting/bson_template_evaluator_test.cpp'],
                LIBDEPS=['bson_template_evaluator'])

if usev8:
    scriptingEnv = env.Clone()
    scriptingEnv.InjectThirdPartyIncludePaths(libraries=['v8'])
    scriptingEnv.Library(
        target='scripting',
        source=[
            'scripting/engine_v8' + v8suffix + '.cpp',
            'scripting/v8' + v8suffix + '_db.cpp',
            'scripting/v8' + v8suffix + '_utils.cpp',
            'scripting/v8' + v8suffix + '_profiler.cpp',
        ],
        LIBDEPS=[
            'bson_template_evaluator',
            'scripting_common',
            '$BUILD_DIR/third_party/shim_v8',
        ],
    )
else:
    env.Library(
        target='scripting',
        source=[
            'scripting/engine_none.cpp',
        ],
        LIBDEPS=[
            'bson_template_evaluator',
            'scripting_common',
        ],
    )

env.Library('update_index_data', [ 'db/update_index_data.cpp' ], LIBDEPS=[ 'db/common' ])

# Global Configuration.  Used by both mongos and mongod.
env.Library('global_environment_experiment',
            [ 'db/global_environment_experiment.cpp',
              'db/global_environment_noop.cpp' ])

# Memory-mapped files support.  Used by mongod and some tools.
env.Library('mmap', ['util/mmap.cpp', 'util/mmap_${OS_FAMILY}.cpp'], LIBDEPS=['foundation'])

env.Library('elapsed_tracker',
            ['util/elapsed_tracker.cpp'],
            LIBDEPS=['foundation',
                     'network'] # this is for using listener to check elapsed time
            )

# mongod files - also files used in tools. present in dbtests, but not in mongos and not in client
# libs.
serverOnlyFiles = [ "db/background.cpp",
                    "db/catalog/collection.cpp",
                    "db/catalog/collection_compact.cpp",
                    "db/catalog/collection_info_cache.cpp",
                    "db/catalog/cursor_manager.cpp",
                    "db/catalog/database.cpp",
                    "db/catalog/database_holder.cpp",
                    "db/catalog/index_catalog.cpp",
                    "db/catalog/index_catalog_entry.cpp",
                    "db/catalog/index_create.cpp",
                    "db/client.cpp",
                    "db/clientcursor.cpp",
                    "db/cloner.cpp",
                    "db/commands/apply_ops.cpp",
                    "db/commands/auth_schema_upgrade_d.cpp",
                    "db/commands/cleanup_orphaned_cmd.cpp",
                    "db/commands/clone.cpp",
                    "db/commands/clone_collection.cpp",
                    "db/commands/collection_to_capped.cpp",
                    "db/commands/compact.cpp",
                    "db/commands/copydb.cpp",
                    "db/commands/copydb_start_commands.cpp",
                    "db/commands/count.cpp",
                    "db/commands/create_indexes.cpp",
                    "db/commands/dbhash.cpp",
                    "db/commands/distinct.cpp",
                    "db/commands/drop_indexes.cpp",
                    "db/commands/explain_cmd.cpp",
                    "db/commands/find_and_modify.cpp",
                    "db/commands/find_cmd.cpp",
                    "db/commands/fsync.cpp",
                    "db/commands/geo_near_cmd.cpp",
                    "db/commands/get_last_error.cpp",
                    "db/commands/group.cpp",
                    "db/commands/index_filter_commands.cpp",
                    "db/commands/list_collections.cpp",
                    "db/commands/list_databases.cpp",
                    "db/commands/list_indexes.cpp",
                    "db/commands/merge_chunks_cmd.cpp",
                    "db/commands/mr.cpp",
                    "db/commands/oplog_note.cpp",
                    "db/commands/parallel_collection_scan.cpp",
                    "db/commands/pipeline_command.cpp",
                    "db/commands/plan_cache_commands.cpp",
                    "db/commands/rename_collection.cpp",
                    "db/commands/repair_cursor.cpp",
                    "db/commands/test_commands.cpp",
                    "db/commands/touch.cpp",
                    "db/commands/validate.cpp",
                    "db/commands/write_commands/batch_executor.cpp",
                    "db/commands/write_commands/write_commands.cpp",
                    "db/commands/writeback_compatibility_shim.cpp",
                    "db/curop.cpp",
                    "db/currentop_command.cpp",
                    "db/dbcommands.cpp",
                    "db/dbdirectclient.cpp",
                    "db/dbeval.cpp",
                    "db/dbhelpers.cpp",
                    "db/driverHelpers.cpp",
                    "db/geo/haystack.cpp",
                    "db/global_environment_d.cpp",
                    "db/index/2d_access_method.cpp",
                    "db/index/btree_access_method.cpp",
                    "db/index/btree_based_access_method.cpp",
                    "db/index/btree_based_bulk_access_method.cpp",
                    "db/index/btree_index_cursor.cpp",
                    "db/index/fts_access_method.cpp",
                    "db/index/hash_access_method.cpp",
                    "db/index/haystack_access_method.cpp",
                    "db/index/s2_access_method.cpp",
                    "db/index_builder.cpp",
                    "db/index_legacy.cpp",
                    "db/index_rebuilder.cpp",
                    "db/instance.cpp",
                    "db/introspect.cpp",
                    "db/matcher/expression_where.cpp",
                    "db/operation_context_impl.cpp",
                    "db/ops/delete.cpp",
                    "db/ops/insert.cpp",
                    "db/ops/parsed_delete.cpp",
                    "db/ops/parsed_update.cpp",
                    "db/ops/update.cpp",
                    "db/ops/update_lifecycle_impl.cpp",
                    "db/ops/update_result.cpp",
                    "db/pipeline/document_source_cursor.cpp",
                    "db/pipeline/pipeline_d.cpp",
                    "db/prefetch.cpp",
                    "db/range_deleter_db_env.cpp",
                    "db/range_deleter_service.cpp",
                    "db/repair_database.cpp",
                    "db/repl/bgsync.cpp",
                    "db/repl/initial_sync.cpp",
                    "db/repl/master_slave.cpp",
                    "db/repl/minvalid.cpp",
                    "db/repl/multicmd.cpp",
                    "db/repl/oplog.cpp",
                    "db/repl/oplogreader.cpp",
                    "db/repl/replication_coordinator_external_state_impl.cpp",
                    "db/repl/replication_info.cpp",
                    "db/repl/replset_commands.cpp",
                    "db/repl/resync.cpp",
                    "db/repl/rs_initialsync.cpp",
                    "db/repl/rs_rollback.cpp",
                    "db/repl/rs_sync.cpp",
                    "db/repl/scoped_conn.cpp",
                    "db/repl/sync.cpp",
                    "db/repl/sync_source_feedback.cpp",
                    "db/repl/sync_tail.cpp",
                    "db/stats/lock_server_status_section.cpp",
                    "db/stats/range_deleter_server_status.cpp",
                    "db/stats/snapshots.cpp",
                    "db/stats/top.cpp",
                    "db/storage/storage_init.cpp",
                    "db/storage_options.cpp",
                    "db/ttl.cpp",
                    "db/write_concern.cpp",
                    "s/d_merge.cpp",
                    "s/d_migrate.cpp",
                    "s/d_split.cpp",
                    "s/d_state.cpp",
                    "s/distlock_test.cpp",
                    "util/compress.cpp",
                    "util/logfile.cpp",
                ]

# This library exists because some libraries, such as our networking library, need access to server
# options, but not to the helpers to set them from the command line.  libserver_options_core.a just
# has the structure for storing the server options, while libserver_options.a has the code to set
# them via the command line.
env.Library("server_options_core", ["db/server_options.cpp"],
            LIBDEPS=['bson'])

env.Library("server_options", [
                    "db/server_options_helpers.cpp"
                    ],
            LIBDEPS=['bson',
                     'network', # temporary crutch that should go away once the networking
                                # library has separate options
                     'server_options_core',
                     'server_parameters',
                     '$BUILD_DIR/mongo/util/cmdline_utils/cmdline_utils',
                     '$BUILD_DIR/mongo/util/options_parser/options_parser',
                    ])

env.CppUnitTest('server_options_test', 'db/server_options_test.cpp',
                LIBDEPS=['server_options'])

env.CppUnitTest('v8_deadline_monitor_test', 'scripting/v8_deadline_monitor_test.cpp', LIBDEPS=[])

env.Library('stacktrace',
            'util/stacktrace_${OS_FAMILY}.cpp',
            LIBDEPS=['bson',
                     'stringutils',
                     'version',
                     '$BUILD_DIR/mongo/base/base'])

env.Library(target='quick_exit',
            source=[
                'util/quick_exit.cpp',
            ])

env.Library('coreshard', [# This is only here temporarily for auto-split logic in chunk.cpp.
                          's/balancer_policy.cpp',
                          's/distlock.cpp',
                          's/config.cpp',
                          's/grid.cpp',
                          's/chunk.cpp',
                          # No good reason to be here other than chunk.cpp needs this.
                          's/config_server_checker_service.cpp',
                          's/shard.cpp',
                          's/shard_key_pattern.cpp'],
            LIBDEPS=['s/base',
                     's/cluster_ops_impl']);

mongosLibraryFiles = [
    "s/strategy.cpp",
    "s/commands_admin.cpp",
    "s/commands_public.cpp",
    "s/commands/auth_schema_upgrade_s.cpp",
    "s/commands/cluster_explain_cmd.cpp",
    "s/commands/cluster_find_cmd.cpp",
    "s/commands/cluster_index_filter_cmd.cpp",
    "s/commands/cluster_merge_chunks_cmd.cpp",
    "s/commands/cluster_plan_cache_cmd.cpp",
    "s/commands/cluster_write_cmd.cpp",
    "s/request.cpp",
    "s/client_info.cpp",
    "s/cursors.cpp",
    "s/s_only.cpp",
    "s/balance.cpp",
    "s/version_manager.cpp",
    "s/version_mongos.cpp",
    ]

env.Library( "mongoscore",
             mongosLibraryFiles,
             LIBDEPS=['db/auth/authmongos',
                      'db/fts/ftsmongos',
                      'db/query/explain_common',
                      'db/query/lite_parsed_query',
                      's/cluster_ops',
                      's/cluster_write_op_conversion',
                      's/upgrade',
                     ] )

env.CppUnitTest("shard_key_pattern_test", [ "s/shard_key_pattern_test.cpp" ],
                LIBDEPS=["mongoscore",
                         "coreshard",
                         "mongocommon",
                         "coreserver",
                         "coredb"])

env.CppUnitTest( "balancer_policy_test" , [ "s/balancer_policy_tests.cpp" ] ,
                LIBDEPS=["mongoscore",
                         "coreshard",
                         "mongocommon",
                         "coreserver",
                         "coredb",
                         "message_server_port"])

env.CppUnitTest("dbclient_rs_test", [ "client/dbclient_rs_test.cpp" ],
                 LIBDEPS=['clientdriver', 'mocklib'])
env.CppUnitTest("scoped_db_conn_test", [ "client/scoped_db_conn_test.cpp" ],
                 LIBDEPS=[
                    "coredb",
                    "coreserver",
                    "coreshard",
                    "mongocommon",
                    "message_server_port",
                    "mongoscore",
                    "ntservice_mock"],
                 NO_CRUTCH=True)

env.CppUnitTest("shard_conn_test", [ "s/shard_conn_test.cpp" ],
                 LIBDEPS=[
                    "mongoscore",
                    "coreshard",
                    "mongocommon",
                    "coreserver",
                    "coredb",
                    "message_server_port",
                    "mocklib",
                    "$BUILD_DIR/mongo/db/auth/authmocks"])

env.CppUnitTest("shard_test", [ "s/shard_test.cpp" ],
                LIBDEPS=[ "mongoscore",
                          "coreshard",
                          "mongocommon",
                          "coreserver",
                          "coredb",
                          "message_server_port",
                          "mocklib"])

env.CppUnitTest('config_server_tests', [ 's/config_server_tests.cpp' ],
                LIBDEPS=[ "mongoscore",
                          "coreshard",
                          "mongocommon",
                          "coreserver",
                          "coredb",
                          "message_server_port",
                          "mocklib"])


# Should only need stuff from util, unittest and platform
env.CppUnitTest("fail_point_test", [ "util/fail_point_test.cpp" ],
                LIBDEPS=["fail_point"])

if has_option( 'use-cpu-profiler' ):
    serverOnlyFiles.append( 'db/commands/cpuprofile.cpp' )
    env.Append(LIBS=['unwind'])
    # If we are building with our internal gperftools, add the necessary include path.
    #
    # NOTE: This is pretty bad because it will spam this include path into many files that
    # don't require it, but because of the way things are currently set up, it is not easy to
    # scope it more narrowly. Better would be if the commands were a library, and could be
    # conditionally made to depend on this file, as a library and then we could easily scope
    # just to this file.
    env.InjectThirdPartyIncludePaths('tcmalloc')

env.Library("defaultversion", "s/default_version.cpp")

env.CppUnitTest(
    target="index_filter_commands_test",
    source=[
        "db/commands/index_filter_commands_test.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/serveronly",
        "$BUILD_DIR/mongo/coreserver",
        "$BUILD_DIR/mongo/coredb",
        "$BUILD_DIR/mongo/ntservice_mock",
    ],
    NO_CRUTCH = True,
)

env.CppUnitTest(
    target="mr_test",
    source=[
        "db/commands/mr_test.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/serveronly",
        "$BUILD_DIR/mongo/coreserver",
        "$BUILD_DIR/mongo/coredb",
        "$BUILD_DIR/mongo/ntservice_mock",
    ],
    NO_CRUTCH = True,
)

env.CppUnitTest(
    target="plan_cache_commands_test",
    source=[
        "db/commands/plan_cache_commands_test.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/serveronly",
        "$BUILD_DIR/mongo/coreserver",
        "$BUILD_DIR/mongo/coredb",
        "$BUILD_DIR/mongo/ntservice_mock",
    ],
    NO_CRUTCH = True,
)

env.Library('range_deleter',
            [ 'db/range_deleter.cpp',
              'db/range_deleter_mock_env.cpp',
            ],
            LIBDEPS = [
                '$BUILD_DIR/mongo/db/repl/repl_coordinator_global',
                '$BUILD_DIR/mongo/s/base', # range_arithmetic.cpp
                'base/base',
                'bson',
                'global_environment_experiment',
                'synchronization'
            ])

env.CppUnitTest('range_deleter_test',
                [ 'db/range_deleter_test.cpp' ],
                LIBDEPS = [
                    '$BUILD_DIR/mongo/db/repl/replmocks',
                    'db/common',
                    'range_deleter',
                ])

serveronlyEnv = env.Clone()
serveronlyEnv.InjectThirdPartyIncludePaths(libraries=['snappy'])
serveronlyLibdeps = ["coreshard",
                     "db/auth/authmongod",
                     "db/fts/ftsmongod",
                     "db/common",
                     "db/concurrency/lock_manager",
                     "db/concurrency/write_conflict_exception",
                     "db/ops/update_driver",
                     "defaultversion",
                     "global_optime",
                     "index_key_validate",
                     'range_deleter',
                     'scripting',
                     "update_index_data",
                     's/metadata',
                     's/batch_write_types',
                     "db/catalog/collection_options",
                     "db/exec/working_set",
                     "db/exec/exec",
                     "db/index/index_descriptor",
                     "db/query/query",
                     "db/repl/repl_settings",
                     "db/repl/network_interface_impl",
                     "db/repl/replication_executor",
                     "db/repl/repl_coordinator_impl",
                     "db/repl/topology_coordinator_impl",
                     "db/repl/repl_coordinator_global",
                     "db/repl/replication_executor",
                     "db/repl/rslog",
                     'db/startup_warnings_mongod',
                     'db/storage/devnull/storage_devnull',
                     'db/storage/in_memory/storage_in_memory',
                     'db/storage/mmap_v1/storage_mmapv1',
                     'db/storage/storage_engine_lock_file',
                     'db/storage/storage_engine_metadata',
                     'mmap',
                     'elapsed_tracker',
                     '$BUILD_DIR/third_party/shim_snappy']

if has_option("rocksdb" ):
    serveronlyLibdeps.append( 'db/storage/rocks/storage_rocks' )

if wiredtiger:
    serveronlyLibdeps.append( 'db/storage/wiredtiger/storage_wiredtiger' )
    serveronlyLibdeps.append( '$BUILD_DIR/third_party/shim_wiredtiger')

serveronlyEnv.Library("serveronly", serverOnlyFiles,
                      LIBDEPS=serveronlyLibdeps )

env.Library("message_server_port", "util/net/message_server_port.cpp")

env.Library("signal_handlers_synchronous",
            ['util/signal_handlers_synchronous.cpp',
             'util/allocator.cpp',],
            LIBDEPS=["stacktrace", "foundation"]
            )

env.Library("signal_handlers",
            ["util/signal_handlers.cpp",],
            LIBDEPS=["foundation", "signal_handlers_synchronous"]
            )

# These files go into mongos and mongod only, not into the shell or any tools.
mongodAndMongosFiles = [
    "db/initialize_server_global_state.cpp",
    "db/server_extra_log_context.cpp",
    "db/dbwebserver.cpp",
    ]
env.Library("mongodandmongos", mongodAndMongosFiles,
            LIBDEPS=["message_server_port", "signal_handlers"])

env.Library("mongodwebserver",
            [
             "db/clientlistplugin.cpp",
             "db/repl/replset_web_handler.cpp",
             "db/restapi.cpp",
             "db/stats/snapshots_webplugins.cpp",
             ],
            LIBDEPS=["coredb",
                     "mongodandmongos",
                     "$BUILD_DIR/mongo/db/repl/repl_coordinator_global"])

mongodOnlyFiles = [ "db/db.cpp", "db/mongod_options_init.cpp" ]

# ----- TARGETS ------

env.Library("gridfs", "client/gridfs.cpp")

env.Library(
    target='coreserver',
    source=[
        'db/client_basic.cpp',
        'db/conn_pool_options.cpp',
        'db/log_process_details.cpp',
        'db/stats/counters.cpp',
        'util/net/miniwebserver.cpp',
    ],
    LIBDEPS=[
        'mongocommon',
    ],
)

# mongod options
env.Library("mongod_options", ["db/mongod_options.cpp"],
            LIBDEPS=['server_options',
                     'mongocommon',
                     'serveronly',
                     'coreserver',
                     'coredb',
                     '$BUILD_DIR/mongo/util/options_parser/options_parser_init'])

# main db target
mongod = env.Install(
    '#/', env.Program( "mongod", mongodOnlyFiles,
                       LIBDEPS=["coredb",
                                "coreserver",
                                "mongodandmongos",
                                "mongodwebserver",
                                "ntservice",
                                "serveronly",
                                "mongod_options",
                                ] ) )
Default( mongod )

# tools
rewrittenTools = [ "mongodump", "mongorestore", "mongoexport", "mongoimport", "mongostat", "mongotop", "bsondump", "mongofiles", "mongooplog" ]

#some special tools
env.Library("mongobridge_options", ["tools/mongobridge_options.cpp"],
            LIBDEPS = [
                'serveronly',
                'coreserver',
                'coredb',
                'signal_handlers_synchronous',
                '$BUILD_DIR/mongo/util/options_parser/options_parser_init',
            ])

env.Install( '#/', [
        env.Program( "mongobridge", ["tools/bridge.cpp", "tools/mongobridge_options_init.cpp"],
                     LIBDEPS=["ntservice_mock", "serveronly", "coredb", "mongobridge_options"] ),
        env.Program( "mongoperf", "client/examples/mongoperf.cpp",
                     LIBDEPS = [
                         "ntservice_mock",
                         "serveronly",
                         "coreserver",
                         "coredb",
                         "signal_handlers_synchronous",
                     ] ),
        ] )

# mongos options
env.Library("mongos_options", ["s/mongos_options.cpp"],
            LIBDEPS=['mongoscore',
                     'coreshard',
                     'mongocommon',
                     'coredb',
                     '$BUILD_DIR/mongo/util/options_parser/options_parser_init'])

# mongos
mongos = env.Program(
    "mongos", [ "s/server.cpp", "s/mongos_options_init.cpp" ] ,
    LIBDEPS=["mongoscore", "coreserver", "coredb", "mongocommon", "coreshard", "ntservice",
             "mongodandmongos", "s/upgrade", "mongos_options" ])
env.Install( '#/', mongos )

env.Library("clientandshell", ["client/clientAndShell.cpp"],
                              LIBDEPS=["mongocommon",
                                       "defaultversion",
                                       "gridfs"])
env.Library("allclient", "client/clientOnly.cpp", LIBDEPS=["clientandshell"])

# dbtests test binary options
env.Library("framework_options", ["dbtests/framework_options.cpp"],
            LIBDEPS=['$BUILD_DIR/mongo/util/options_parser/options_parser_init'])

# dbtests test binary
env.Library('testframework', ['dbtests/framework.cpp', 'dbtests/framework_options_init.cpp'],
            LIBDEPS=['unittest/unittest',
            'framework_options',
            ])

env.Library('mocklib', [
        'dbtests/mock/mock_conn_registry.cpp',
        'dbtests/mock/mock_dbclient_connection.cpp',
        'dbtests/mock/mock_dbclient_cursor.cpp',
        'dbtests/mock/mock_remote_db_server.cpp',
        'dbtests/mock/mock_replica_set.cpp'
    ],
    LIBDEPS=['clientdriver',
             '$BUILD_DIR/mongo/db/repl/replica_set_messages'])

test = env.Install(
    '#/',
    env.Program("dbtest",
                    [ f for f in Glob("dbtests/*.cpp")
                      if not str(f).endswith('framework.cpp') and
                         not str(f).endswith('framework_options.cpp') and
                         not str(f).endswith('framework_options_init.cpp') ],
                    LIBDEPS = [
                       "mutable_bson_test_utils",
                       "mongocommon",
                       "serveronly",
                       "coreserver",
                       "coredb",
                       "testframework",
                       "gridfs",
                       "signal_handlers_synchronous",
                       "s/upgrade",
                       "s/cluster_ops",
                       "s/cluster_ops_impl",
                       "mocklib",
                       "$BUILD_DIR/mongo/db/auth/authmocks",
                       "$BUILD_DIR/mongo/db/query/query",
                       "$BUILD_DIR/mongo/db/repl/repl_coordinator_global",
                       "$BUILD_DIR/mongo/db/repl/replmocks"]))

if len(env.subst('$PROGSUFFIX')):
    env.Alias( "dbtest", "#/${PROGPREFIX}dbtest${PROGSUFFIX}" )

env.Install('$BUILD_ROOT/', env.Program('file_allocator_bench',
            'util/file_allocator_bench.cpp',
            LIBDEPS=[
                'mongocommon',
                'signal_handlers_synchronous',
                '$BUILD_DIR/mongo/util/options_parser/options_parser_init',
                'serveronly',
                'coredb',
                'coreserver',
                "ntservice_mock",
            ]))

env.Alias('file_allocator_bench', "$BUILD_ROOT/" + add_exe("file_allocator_bench"))

# --- sniffer ---
mongosniff_built = False
if env["_HAVEPCAP"]:
    mongosniff_built = True
    sniffEnv = env.Clone()
    sniffEnv.Append( CPPDEFINES="MONGO_EXPOSE_MACROS" )

    sniffEnv.Append( LIBS=[ "pcap" ] )

    sniffEnv.Install( '#/', sniffEnv.Program( "mongosniff", "tools/sniffer.cpp",
                                              LIBDEPS = [
                                                 "gridfs",
                                                 "serveronly",
                                                 "coreserver",
                                                 "coredb",
                                                 "signal_handlers_synchronous",
                                              ] ) )

# --- shell ---

# if you add a file here, you need to add it in scripting/engine.cpp and shell/createCPPfromJavaScriptFiles.js as well
env.JSHeader(
            target="shell/mongo.cpp",
            source=[
                "shell/assert.js",
                "shell/bulk_api.js",
                "shell/collection.js",
                "shell/db.js",
                "shell/explain_query.js",
                "shell/explainable.js",
                "shell/mongo.js",
                "shell/mr.js",
                "shell/query.js",
                "shell/types.js",
                "shell/upgrade_check.js",
                "shell/utils.js",
                "shell/utils_sh.js",
                "shell/utils_auth.js",
            ])

# if you add a file here, you need to add it in shell/shell_utils.cpp and shell/createCPPfromJavaScriptFiles.js as well
env.JSHeader(
            target="shell/mongo-server.cpp",
            source=[
                "shell/servers.js",
                "shell/mongodtest.js",
                "shell/shardingtest.js",
                "shell/servers_misc.js",
                "shell/replsettest.js",
                "shell/replsetbridge.js"
             ])

coreShellFiles = [ "shell/bench.cpp",
                   "shell/shell_utils.cpp",
                   "shell/shell_utils_extended.cpp",
                   "shell/shell_utils_launcher.cpp",
                   "shell/mongo-server.cpp",
                   "shell/linenoise.cpp",
                   "shell/linenoise_utf8.cpp",
                   "shell/mk_wcwidth.cpp",
                   "shell/shell_options_init.cpp" ]

if not has_option('noshell'):
    env.Library("shell_core", coreShellFiles,
                LIBDEPS=['clientandshell',
                         'db/index/external_key_generator',
                         'index_key_validate',
                         'scripting',
                         "signal_handlers",
                         'mongocommon'])
    # mongo shell options
    env.Library("shell_options", ["shell/shell_options.cpp"],
                LIBDEPS=['$BUILD_DIR/mongo/util/options_parser/options_parser_init'])

    shellEnv = env.Clone()

    mongo_shell = shellEnv.Program(
        "mongo",
        "shell/dbshell.cpp",
        LIBDEPS=["$BUILD_DIR/third_party/shim_pcrecpp",
                 "shell_options",
                 "shell_core",
                 ])

    shellEnv.Install( '#/', mongo_shell )

#  ----  INSTALL -------

# binaries

distBinaries = []
distDebugSymbols = []

def add_exe( v ):
    return "${PROGPREFIX}%s${PROGSUFFIX}" % v

def failMissingObjCopy(env, target, source):
    env.FatalError("Generating debug symbols requires objcopy, please set the OBJCOPY variable.")

def installBinary( e, name ):
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
        e.Install("#/", debug_sym)
        e.Alias('debugsymbols', debug_sym)
        distDebugSymbols.append(debug_sym)

    if not has_option("nostrip"):
        strip_cmd = e.Command(
            'stripped/%s' % name,
            [name, debug_sym],
            '${OBJCOPY} --strip-debug --add-gnu-debuglink ${SOURCES[1]} ${SOURCES[0]} $TARGET'
        )
        distBinaries.append('stripped/%s' % name)
    else:
        distBinaries.append(name)

    inst = e.Install( "$INSTALL_DIR/bin", name )

    e.AddPostAction( inst, 'chmod 755 $TARGET' )

def installExternalBinary( e, name_str ):
    name = env.File("#/%s" % add_exe(name_str))
    if not name.isfile():
        print("ERROR: external binary not found: %s" % name)
        Exit(1)

    distBinaries.append(name)
    inst = e.Install( "$INSTALL_DIR/bin", name )

    e.AddPostAction( inst, 'chmod 755 $TARGET' )


# "--use-new-tools" adds dependencies for rewritten (Go) tools
# It is required for "dist" but optional for "install"
if has_option("use-new-tools"):
    toolsRoot = "src/mongo-tools"
    for t in rewrittenTools:
        installExternalBinary(env, "%s/%s" % (toolsRoot, t))

# legacy tools
installBinary(env, "mongoperf")
env.Alias("tools", '#/' + add_exe("mongoperf"))

env.Alias("tools", "#/" + add_exe("mongobridge"))

if mongosniff_built:
    installBinary(env, "mongosniff")
    env.Alias("tools", '#/' + add_exe("mongosniff"))

installBinary( env, "mongod" )
installBinary( env, "mongos" )

if shellEnv is not None:
    installBinary( shellEnv, "mongo" )

env.Alias( "core", [ '#/%s' % b for b in [ add_exe( "mongo" ), add_exe( "mongod" ), add_exe( "mongos" ) ] ] )

# Stage the top-level mongodb banners
distsrc = env.Dir('#distsrc')
env.Append(MODULE_BANNERS = [distsrc.File('README'),
                             distsrc.File('THIRD-PARTY-NOTICES')])

# If no module has introduced a file named LICENSE.txt, then inject the AGPL.
if sum(itertools.imap(lambda x: x.name == "LICENSE.txt", env['MODULE_BANNERS'])) == 0:
    env.Append(MODULE_BANNERS = [distsrc.File('GNU-AGPL-3.0')])

# All module banners get staged to the top level of the tarfile, so we
# need to fail if we are going to have a name collision.
module_banner_filenames = set([f.name for f in env['MODULE_BANNERS']])
if not len(module_banner_filenames) == len(env['MODULE_BANNERS']):
    # TODO: Be nice and identify conflicts in error.
    print "ERROR: Filename conflicts exist in module banners."
    Exit(-1)

# Build a set of directories containing module banners, and use that
# to build a --transform option for each directory so that the files
# are tar'ed up to the proper location.
module_banner_dirs = set([Dir('#').rel_path(f.get_dir()) for f in env['MODULE_BANNERS']])
module_banner_transforms = ["--transform %s=$SERVER_DIST_BASENAME" % d for d in module_banner_dirs]

# Allow modules to map original file name directories to subdirectories 
# within the archive (e.g. { "src/mongo/db/modules/enterprise/docs": "snmp"})
archive_addition_transforms = []
for full_dir, archive_dir in env["ARCHIVE_ADDITION_DIR_MAP"].items():
  archive_addition_transforms.append("--transform \"%s=$SERVER_DIST_BASENAME/%s\"" %
                                     (full_dir, archive_dir))

# "dist" target is valid only when --use-new-tools is specified
# Attempts to build release artifacts without tools must fail
if has_option("use-new-tools"):
    env.Command(
        '#/${SERVER_ARCHIVE}',
        ['#buildscripts/make_archive.py'] + env["MODULE_BANNERS"] + env["ARCHIVE_ADDITIONS"] +
        distBinaries, ' '.join(['$PYTHON ${SOURCES[0]} -o $TARGET'] + archive_addition_transforms +
        module_banner_transforms + [
                '--transform ${str(Dir(BUILD_DIR))}/mongo/stripped=$SERVER_DIST_BASENAME/bin',
                '--transform ${str(Dir(BUILD_DIR))}/mongo=$SERVER_DIST_BASENAME/bin',
                '--transform ${str(Dir(BUILD_DIR))}/mongo/stripped/src/mongo-tools=$SERVER_DIST_BASENAME/bin',
                '--transform src/mongo-tools=$SERVER_DIST_BASENAME/bin',
                '${TEMPFILE(SOURCES[1:])}']))

    env.Alias("dist", source='#/${SERVER_ARCHIVE}')
else:
    def failDist(env, target, source):
        print("ERROR: 'dist' target only valid with --use-new-tools.")
        Exit(1)
    env.Alias("dist", [], [ failDist ] )
    env.AlwaysBuild("dist")

debug_symbols_dist = env.Command(
    target='#/${SERVER_DIST_BASENAME}-debugsymbols${DIST_ARCHIVE_SUFFIX}',
    source=['#buildscripts/make_archive.py'] + distDebugSymbols,
    action='$PYTHON ${SOURCES[0]} -o $TARGET --transform $BUILD_DIR/mongo=$SERVER_DIST_BASENAME ${TEMPFILE(SOURCES[1:])}',
    BUILD_DIR=env.Dir('$BUILD_DIR').path
)
env.Alias('dist-debugsymbols', debug_symbols_dist)

#final alias
env.Alias( "install", "$INSTALL_DIR" )
