# -*- mode: python -*-

Import("endian")
Import("env")
Import("get_option")
Import("has_option")

env = env.Clone()

env.InjectThirdPartyIncludePaths('asio')
env.InjectThirdPartyIncludePaths('valgrind')

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

debuggerEnv = env.Clone()
if has_option("gdbserver"):
    debuggerEnv.Append(CPPDEFINES=["USE_GDBSERVER"])

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

env.CppUnitTest(
    target='decorable_test',
    source=[
        'decorable_test.cpp'
        ],
    LIBDEPS=[
        ]
    )

env.CppUnitTest(
    target='represent_as_test',
    source=[
        'represent_as_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/third_party/shim_boost',
    ],
)

env.CppUnitTest(
    target='lru_cache_test',
    source=[
        'lru_cache_test.cpp',
    ],
    LIBDEPS=[
    ],
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

env.CppUnitTest(
    target='summation_test',
    source=[
        'summation_test.cpp',
    ],
    LIBDEPS=[
        'summation',
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/third_party/shim_boost',
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

env.CppUnitTest(
    target='progress_meter_test',
    source=[
        'progress_meter_test.cpp',
    ],
    LIBDEPS=[
        'progress_meter',
    ],
)

env.Library(
    target='md5',
    source=[
        'md5.cpp',
        'password_digest.cpp',
    ],
)

env.CppUnitTest(
    target="md5_test",
    source=[
        "md5_test.cpp",
        "md5main.cpp",
    ],
    LIBDEPS=[
        "md5",
    ],
)

env.Library(
    target='clock_source_mock',
    source=[
        'clock_source_mock.cpp',
        'tick_source_mock.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='clock_source_mock_test',
    source=[
        'clock_source_mock_test.cpp',
    ],
    LIBDEPS=[
        'clock_source_mock',
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

env.CppUnitTest(
    target='alarm_test',
    source=[
        'alarm_test.cpp',
    ],
    LIBDEPS=[
        'alarm',
        'clock_source_mock',
    ]
)

env.CppUnitTest(
    target='text_test',
    source=[
        'text_test.cpp'
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='time_support_test',
    source=[
        'time_support_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target="stringutils_test",
    source=[
        "stringutils_test.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
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

env.CppUnitTest(
    target="processinfo_test",
    source=[
        "processinfo_test.cpp",
    ],
    LIBDEPS=[
        "processinfo",
    ],
)

env.Library(
    target="fail_point",
    source=[
        "fail_point.cpp",
        "fail_point_registry.cpp",
        "fail_point_server_parameter.cpp",
        "fail_point_service.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
        "$BUILD_DIR/mongo/bson/util/bson_extract",
        "$BUILD_DIR/mongo/db/server_parameters",
    ],
)

env.CppUnitTest(
    target="fail_point_test",
    source=[
        "fail_point_test.cpp",
    ],
    LIBDEPS=[
        "fail_point",
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

env.CppUnitTest(
    target="periodic_runner_impl_test",
    source=[
        "periodic_runner_impl_test.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/db/service_context_test_fixture",
        "clock_source_mock",
        "periodic_runner_impl",
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

env.CppUnitTest(
    target="background_job_test",
    source=[
        "background_job_test.cpp",
    ],
    LIBDEPS=[
        "background_job",
    ],
)

if env['MONGO_ALLOCATOR'] == 'tcmalloc':
    tcmspEnv = env.Clone()

    tcmspEnv.Library(
        target='tcmalloc_set_parameter',
        source=[
            'tcmalloc_server_status_section.cpp',
            'tcmalloc_set_parameter.cpp',
            'heap_profiler.cpp',
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/db/server_parameters',
            '$BUILD_DIR/mongo/transport/service_executor',
        ],
        LIBDEPS_PRIVATE=[
            '$BUILD_DIR/mongo/db/commands/server_status',
            'processinfo',
        ],
        LIBDEPS_DEPENDENTS=[
            '$BUILD_DIR/mongo/mongodmain',
        ],
        PROGDEPS_DEPENDENTS=[
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

env.CppUnitTest(
    target='background_thread_clock_source_test',
    source=[
        'background_thread_clock_source_test.cpp',
    ],
    LIBDEPS=[
        'clock_source_mock',
        'clock_sources',
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

if has_option('use-cpu-profiler'):
    quick_exit_env.Append(
        CPPDEFINES=[
            'MONGO_CPU_PROFILER',
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

env.CppUnitTest(
    target='dns_query_test',
    source=['dns_query_test.cpp'],
    LIBDEPS=[
        'dns_query',
        "$BUILD_DIR/mongo/base",
    ],
)

env.CppUnitTest(
    target='dns_name_test',
    source=['dns_name_test.cpp'],
    LIBDEPS=[
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

env.CppUnitTest(
    target='secure_zero_memory_test',
    source=['secure_zero_memory_test.cpp'],
    LIBDEPS=[
        'secure_zero_memory'
    ],
)

env.CppUnitTest(
    target='signal_handlers_synchronous_test',
    source=[
        'signal_handlers_synchronous_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.Library(
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

env.CppUnitTest(
    target="unowned_ptr_test",
    source=[
        "unowned_ptr_test.cpp",
    ],
    LIBDEPS=[
        # None since unowned_ptr is header-only.
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

env.CppUnitTest(
    target='safe_num_test',
    source=[
        'safe_num_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        'safe_num',
    ],
)

env.CppUnitTest(
    target='string_map_test',
    source=[
        'string_map_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.Library(
    target='password',
    source=[
        'password.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='itoa_test',
    source=[
        'itoa_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ]
)

env.Library(
    target='container_size_helper',
    source=[
        'container_size_helper.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='container_size_helper_test',
    source=[
        'container_size_helper_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ]
)

env.CppUnitTest(
    target='producer_consumer_queue_test',
    source=[
        'producer_consumer_queue_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/db/service_context',
    ]
)

env.CppUnitTest(
    target='duration_test',
    source=[
        'duration_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ])

env.CppUnitTest(
    target='assert_util_test',
    source=[
        'assert_util_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ]
)

env.CppUnitTest(
    target='base64_test',
    source=[
        'base64_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='future_test',
    source=[
        'future_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='keyed_executor_test',
    source=[
        'keyed_executor_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/util/concurrency/thread_pool',
    ],
)

env.CppUnitTest(
    target='strong_weak_finish_line_test',
    source=[
        'strong_weak_finish_line_test.cpp'
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='errno_util_test',
    source=[
        'errno_util_test.cpp',
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

env.Library(
    target='procparser',
    source=[
        "procparser.cpp",
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='procparser_test',
    source=[
        'procparser_test.cpp',
    ],
    LIBDEPS=[
        'procparser',
    ])

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
    target='icu_test',
    source=[
        'icu_test.cpp',
    ],
    LIBDEPS=[
        'icu',
    ],
)
