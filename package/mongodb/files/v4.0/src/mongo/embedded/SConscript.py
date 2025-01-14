# -*- mode: python; -*-

import re

Import("env")
Import("get_option")

env = env.Clone()

env.AppendUnique(
    CPPPATH=["$BUILD_DIR/mongo/embedded"],
)

# Inject this before we call the framework directory SConscripts so that
# they can both use it.

frameworksEnv = env.Clone()

def mongo_export_file_generator(target, source, env, for_signature):
    script = env.File(env.subst("${TARGET.base}.version_script", target=target))
    return script.get_csig() if for_signature else "-Wl,--version-script," + str(script)
frameworksEnv['MONGO_EXPORT_FILE_SHLINKFLAGS'] = mongo_export_file_generator

# We need to set our bundle version in the plist file, but the format
# is contrained to major.minor.patch. So trim off any '-pre' or '-rc'
# information from the MONGO_VERSION and rename it to
# MONGO_BUNDLE_VERSION.
frameworksEnv['PLIST_MONGO_BUNDLE_VERSION'] = env['MONGO_VERSION'].split('-')[0]

# Similarly, we need to derive a MinimumOSVersion based on the
# -mXXX-version-minimum flag. Really, we should pull this out into an
# SCons flag like OSX_DEPLOYMENT_TARGET so we don't need to grub
# around in the flags.
frameworksEnv['PLIST_MINIMUM_OS_VERSION'] = "0.0"
for flag in frameworksEnv['CCFLAGS']:
    if re.search('-m[a-z]+-version-min', flag):
        frameworksEnv['PLIST_MINIMUM_OS_VERSION'] = flag.split('=')[1]
        break

env.SConscript(
    dirs=[
        'mongo_embedded',
        'mongoc_embedded',
    ],
    exports={
        'env' : frameworksEnv,
    },
)

yamlEnv = env.Clone()
yamlEnv.InjectThirdPartyIncludePaths(libraries=['yaml'])

env.Library(
    target='embedded',
    source=[
        'embedded.cpp',
        'embedded_auth_manager.cpp',
        'embedded_auth_session.cpp',
        'embedded_ismaster.cpp',
        'embedded_options.cpp',
        'embedded_options_init.cpp',
        'embedded_options_parser_init.cpp',
        'periodic_runner_embedded.cpp',
        'replication_coordinator_embedded.cpp',
        'service_entry_point_embedded.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/auth/auth',
        '$BUILD_DIR/mongo/db/catalog/catalog_impl',
        '$BUILD_DIR/mongo/db/command_can_run_here',
        '$BUILD_DIR/mongo/db/commands',
        '$BUILD_DIR/mongo/db/commands/fsync_locked',
        '$BUILD_DIR/mongo/db/commands/mongod_fcv',
        '$BUILD_DIR/mongo/db/commands/standalone',
        '$BUILD_DIR/mongo/db/concurrency/lock_manager',
        '$BUILD_DIR/mongo/db/logical_session_cache',
        '$BUILD_DIR/mongo/db/logical_session_cache_impl',
        '$BUILD_DIR/mongo/db/op_observer_impl',
        '$BUILD_DIR/mongo/db/repair_database_and_check_version',
        '$BUILD_DIR/mongo/db/repl/repl_coordinator_interface',
        '$BUILD_DIR/mongo/db/repl/replica_set_messages',
        '$BUILD_DIR/mongo/db/repl/storage_interface_impl',
        '$BUILD_DIR/mongo/db/rw_concern_d',
        '$BUILD_DIR/mongo/db/s/sharding_api_d',
        '$BUILD_DIR/mongo/db/s/sharding_runtime_d_embedded',
        '$BUILD_DIR/mongo/db/server_options',
        '$BUILD_DIR/mongo/db/service_context',
        '$BUILD_DIR/mongo/db/service_entry_point_common',
        '$BUILD_DIR/mongo/db/service_liaison_mongod',
        '$BUILD_DIR/mongo/db/sessions_collection_standalone',
        '$BUILD_DIR/mongo/db/storage/mobile/storage_mobile',
        '$BUILD_DIR/mongo/db/storage/storage_engine_common',
        '$BUILD_DIR/mongo/db/storage/storage_engine_lock_file',
        '$BUILD_DIR/mongo/db/storage/storage_engine_metadata',
        '$BUILD_DIR/mongo/db/storage/storage_init_d',
        '$BUILD_DIR/mongo/db/storage/storage_options',
        '$BUILD_DIR/mongo/db/wire_version',
        '$BUILD_DIR/mongo/rpc/client_metadata',
        '$BUILD_DIR/mongo/util/options_parser/options_parser',
        '$BUILD_DIR/mongo/util/version_impl',
    ]
)

env.Library(
    target='embedded_integration_helpers',
    source=[
        'embedded_options_helpers.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/util/options_parser/options_parser',
    ],
)
