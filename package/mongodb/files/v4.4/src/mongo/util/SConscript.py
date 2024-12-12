# -*- mode: python -*-

Import("endian")
Import("env")
Import("get_option")
Import("has_option")
Import("use_libunwind")

env = env.Clone()

env.InjectThirdParty('asio')
env.InjectThirdParty('valgrind')

env.SConscript(
    dirs=[
        'cmdline_utils',
        'concurrency',
        'net',
        'options_parser',
    ],
    exports=[
        'env',
    ],
)

env.Library(
    target='version_impl',
    source=[
        'version_impl.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ]
)

env.Library(
    target='intrusive_counter',
    source=[
        'intrusive_counter.cpp',
        ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ]
)

env.Library(
    target='log_and_backoff',
    source= [
        'log_and_backoff.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.Library(
    target='regex_util',
    source= [
        'regex_util.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

debuggerEnv = env.Clone()
if has_option("gdbserver"):
    debuggerEnv.Append(CPPDEFINES=["USE_GDBSERVER"])
elif has_option("lldb-server"):
    debuggerEnv.Append(CPPDEFINES=["USE_LLDB_SERVER"])

debuggerEnv.Library(
    target='debugger',
    source=[
        'debugger.cpp',
        ],
    LIBDEPS=[
        # NOTE: You *must not* add any library dependencies to the debugger library
    ],
    LIBDEPS_TAGS=[
        'init-no-global-side-effects',
    ]
)

env.Library(
    target='summation',
    source=[
        'summation.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.Library(
    target='progress_meter',
    source=[
        'progress_meter.cpp',
        'thread_safe_string.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.Library(
    target='md5',
    source=[
        'md5.cpp',
        'password_digest.cpp',
    ],
)

env.Library(
    target='clock_source_mock',
    source=[
        'clock_source_mock.cpp'
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.Library(
    target='alarm',
    source=[
        'alarm.cpp',
        'alarm_runner_background_thread.cpp',
    ],
    LIBDEPS=[
        'clock_sources',
        '$BUILD_DIR/mongo/base',
    ],
)

env.Library(
    target="processinfo",
    source=[
        "processinfo.cpp",
        "processinfo_${TARGET_OS}.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
    ],
)

env.Library(
    target="fail_point",
    source=[
        "fail_point.cpp",
        env.Idlc('fail_point_server_parameter.idl')[0],
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
        "$BUILD_DIR/mongo/bson/util/bson_extract",
        "$BUILD_DIR/mongo/idl/server_parameter",
    ],
)

env.Library(
    target="periodic_runner",
    source=[
        "periodic_runner.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
    ],
)

env.Library(
    target="periodic_runner_impl",
    source=[
        "periodic_runner_impl.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
        "$BUILD_DIR/mongo/db/service_context",
        "periodic_runner",
    ],
)

env.Library(
    target='periodic_runner_factory',
    source=[
        'periodic_runner_factory.cpp',
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/db/service_context",
        'periodic_runner',
        'periodic_runner_impl',
    ],
)

env.Library(
    target='background_job',
    source=[
        "background.cpp",
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        'concurrency/spin_lock',
    ],
)

env.Library(
    target='caching',
    source=[
        'read_through_cache.cpp',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/db/service_context',
    ]
)

env.CppUnitTest(
    target='thread_safety_context_test',
    source=[
        'thread_safety_context_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

if env['MONGO_ALLOCATOR'] in ['tcmalloc', 'tcmalloc-experimental']:
    tcmspEnv = env.Clone()

    tcmspEnv.Library(
        target='tcmalloc_set_parameter',
        source=[
            'tcmalloc_server_status_section.cpp',
            'tcmalloc_set_parameter.cpp',
            env.Idlc('tcmalloc_parameters.idl')[0],
            'heap_profiler.cpp',
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/transport/service_executor',
        ],
        LIBDEPS_PRIVATE=[
            '$BUILD_DIR/mongo/db/commands/server_status',
            '$BUILD_DIR/mongo/idl/server_parameter',
            'processinfo',
        ],
        PROGDEPS_DEPENDENTS=[
            '$BUILD_DIR/mongo/mongod',
            '$BUILD_DIR/mongo/mongos',
        ],
    )

env.Library(
    target='winutil',
    source=[
        'winutil.cpp',
    ],
)

env.Library(
    target='ntservice',
    source=[
        'ntservice.cpp',
    ],
    LIBDEPS=[
        'signal_handlers',
        '$BUILD_DIR/mongo/util/options_parser/options_parser',
    ],
)

env.Library(
    target='clock_sources',
    source=[
        'background_thread_clock_source.cpp',
        'clock_source.cpp',
        'fast_clock_source_factory.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

if get_option('use-diagnostic-latches') == 'on':
    env.Library(
        target='diagnostic_info',
        source= [
            'diagnostic_info.cpp',
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/base',
            "$BUILD_DIR/mongo/db/service_context",
        ],
    )

    env.Library(
        target='latch_analyzer',
        source= [
            'latch_analyzer.cpp',
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/base',
            '$BUILD_DIR/mongo/db/commands/test_commands_enabled',
            '$BUILD_DIR/mongo/db/service_context',
        ],
        LIBDEPS_PRIVATE=[
            '$BUILD_DIR/mongo/db/commands/server_status',
        ],
    )

env.Benchmark(
    target='clock_source_bm',
    source=[
        'clock_source_bm.cpp',
    ],
    LIBDEPS=[
        'clock_sources',
        'processinfo',
    ],
)

env.Library(
    target='elapsed_tracker',
    source=[
        'elapsed_tracker.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        'net/network', # this is for using listener to check elapsed time
    ],
)

quick_exit_env = env.Clone()
if has_option('gcov'):
    quick_exit_env.Append(
        CPPDEFINES=[
            'MONGO_GCOV',
        ],
    )

quick_exit_env.Library(
    target='quick_exit',
    source=[
        'quick_exit.cpp',
    ],
    LIBDEPS=[
        # NOTE: You *must not* add any other library dependencies to
        # the quick_exit library
        "$BUILD_DIR/third_party/shim_allocator",
    ]
)
env.Library(
    target="secure_compare_memory",
    source=[
        'secure_compare_memory.cpp',
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
    ],
)

env.Library(
    target='dns_query',
    source=[
        'dns_query.cpp',
    ],
    LIBDEPS_PRIVATE=[
        "$BUILD_DIR/mongo/base",
    ],
)

env.Library(
    target="secure_zero_memory",
    source=[
        'secure_zero_memory.cpp',
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
    ],
)

signalEnv = env.Clone()

if use_libunwind:
    signalEnv.InjectThirdParty('unwind')

signalEnv.Library(
    target="signal_handlers",
    source=[
        "signal_handlers.cpp",
        "signal_win32.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
        "$BUILD_DIR/mongo/db/log_process_details",
        "$BUILD_DIR/mongo/db/service_context",
        "$BUILD_DIR/mongo/db/server_options_core",
    ],
)

env.Library(
    target='safe_num',
    source=[
        'safe_num.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.Library(
    target='password',
    source=[
        'password.cpp',
        env.Idlc('password_params.idl')[0],
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/idl/server_parameter',
    ]
)


env.Benchmark(
    target='decimal_counter_bm',
    source=[
        'decimal_counter_bm.cpp',
    ],
    LIBDEPS=[
    ],
)

env.Benchmark(
    target='itoa_bm',
    source=[
        'itoa_bm.cpp',
    ],
    LIBDEPS=[
    ],
)

env.Benchmark(
    target='future_bm',
    source=[
        'future_bm.cpp',
    ],
    LIBDEPS=[
    ],
)

env.Benchmark(
    target='hash_table_bm',
    source='hash_table_bm.cpp',
    LIBDEPS=[
    ],
)

env.Library(
    target='procparser',
    source=[
        "procparser.cpp",
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

icuEnv = env.Clone()

# When using ICU from third_party, icu_init.cpp will load a subset of
# ICU's data files using udata_setCommonData() in an initializer.
# When using the system ICU, we rely on those files being in the install path.
icuEnv.Library(
    target='icu_init',
    source=[
        'icu_init_stub.cpp',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/third_party/shim_icu',
    ],
)

icuEnv.Library(
    target='icu',
    source=[
        'icu.cpp',
    ],
    LIBDEPS_PRIVATE=[
        'icu_init',
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/third_party/shim_icu',
    ],
)

icuEnv.CppUnitTest(
    target='util_test',
    source=[
        'alarm_test.cpp',
        'assert_util_test.cpp',
        'background_job_test.cpp',
        'background_thread_clock_source_test.cpp',
        'base64_test.cpp',
        'clock_source_mock_test.cpp',
        'concepts_test.cpp',
        'container_size_helper_test.cpp',
        'decimal_counter_test.cpp',
        'decorable_test.cpp',
        'diagnostic_info_test.cpp' if get_option('use-diagnostic-latches') == 'on' else [],
        'dns_name_test.cpp',
        'dns_query_test.cpp',
        'duration_test.cpp',
        'errno_util_test.cpp',
        'fail_point_test.cpp',
        'future_test_edge_cases.cpp',
        'future_test_executor_future.cpp',
        'future_test_future_int.cpp',
        'future_test_future_move_only.cpp',
        'future_test_future_void.cpp',
        'future_test_promise_int.cpp',
        'future_test_promise_void.cpp',
        'future_test_shared_future.cpp',
        'future_util_test.cpp',
        'hierarchical_acquisition_test.cpp',
        'icu_test.cpp',
        'invalidating_lru_cache_test.cpp',
        'interruptible_test.cpp',
        'itoa_test.cpp',
        'latch_analyzer_test.cpp' if get_option('use-diagnostic-latches') == 'on' else [],
        'lockable_adapter_test.cpp',
        'log_with_sampling_test.cpp',
        'lru_cache_test.cpp',
        'md5_test.cpp',
        'md5main.cpp',
        'out_of_line_executor_test.cpp',
        'periodic_runner_impl_test.cpp',
        'processinfo_test.cpp',
        'procparser_test.cpp',
        'producer_consumer_queue_test.cpp',
        'progress_meter_test.cpp',
        'read_through_cache_test.cpp',
        'registry_list_test.cpp',
        'represent_as_test.cpp',
        'safe_num_test.cpp',
        'secure_zero_memory_test.cpp',
        'signal_handlers_synchronous_test.cpp',
        'str_test.cpp',
        'string_map_test.cpp',
        'strong_weak_finish_line_test.cpp',
        'summation_test.cpp',
        'text_test.cpp',
        'tick_source_test.cpp',
        'time_support_test.cpp',
        'unique_function_test.cpp',
        'unowned_ptr_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/db/service_context_test_fixture',
        '$BUILD_DIR/mongo/executor/thread_pool_task_executor_test_fixture',
        'alarm',
        'background_job',
        'caching',
        'clock_source_mock',
        'clock_sources',
        'concurrency/thread_pool',
        'diagnostic_info' if get_option('use-diagnostic-latches') == 'on' else [],
        'dns_query',
        'fail_point',
        'icu',
        'latch_analyzer' if get_option('use-diagnostic-latches') == 'on' else [],
        'md5',
        'periodic_runner_impl',
        'processinfo',
        'procparser',
        'progress_meter',
        'safe_num',
        'secure_zero_memory',
        'summation',
    ],
)

env.Benchmark(
    target='base64_bm',
    source='base64_bm.cpp',
)

stacktraceEnv = env.Clone()
if use_libunwind:
    stacktraceEnv.InjectThirdParty(libraries=['unwind'])

stacktraceEnv.CppUnitTest(
    target='stacktrace_test',
    source='stacktrace_test.cpp',
)

stacktraceEnv.Benchmark(
    target='stacktrace_bm',
    source='stacktrace_bm.cpp',
)

if use_libunwind:
    unwindTestEnv = env.Clone()
    unwindTestEnv.InjectThirdParty(libraries=['unwind'])
    unwindTestEnv.CppUnitTest(
        target=[
            'stacktrace_libunwind_test',
        ],
        source=[
            'stacktrace_libunwind_test_functions.cpp',
            'stacktrace_libunwind_test.cpp',
        ],
        LIBDEPS=[
            '$BUILD_DIR/third_party/shim_unwind',
        ],
    )
