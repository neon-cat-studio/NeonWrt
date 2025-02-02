# -*- mode: python -*-

Import("env")

env = env.Clone()

env.InjectThirdParty('absl')

env.Benchmark(
    target='condition_variable_bm',
    source=[
        'condition_variable_bm.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.Library(
    target='stdx',
    source=[
        'set_terminate_internals.cpp',
    ],
    LIBDEPS=[
        # Ideally, there should be no linking dependencies upon any other libraries, for `libstdx`.
        # This library is a shim filling in for deficiencies in various standard library
        # implementations.  There should never be any link-time dependencies into mongo internals.
    ],
)

env.CppUnitTest(
    target='stdx_test',
    source=[
        'unordered_map_test.cpp'
    ],
    LIBDEPS=[
        '$BUILD_DIR/third_party/shim_abseil',
    ],
)

# Specify UNITTEST_HAS_CUSTOM_MAINLINE because it needs low-level control of
# thread creation and signals, so it shouldn't use unittest_main and typical
# mongo startup routines.
env.CppUnitTest(
    target='sigaltstack_location_test',
    source=[
        'sigaltstack_location_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    UNITTEST_HAS_CUSTOM_MAINLINE=True,
)

# The tests for `stdx::set_terminate` need to run outside of the mongo unittest harneses.
# The tests require altering the global `set_terminate` handler, which our unittest framework
# doesn't expect to have happen.  Further, the tests have to return successfully from a
# terminate condition which interacts poorly with the unittest framework.
#
# A set of dedicated binaries to each test case is actually the simplest way to accomplish
# robust testing of this mechanism.

# Needs to be a different test -- It has to have direct control over the `main()` entry point.
env.CppUnitTest(
    target='set_terminate_dispatch_test',
    source=[
        'set_terminate_dispatch_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    UNITTEST_HAS_CUSTOM_MAINLINE=True,
)

# Needs to be a different test -- It has to have direct control over the `main()` entry point.
env.CppUnitTest(
    target='set_terminate_from_main_die_in_thread_test',
    source=[
        'set_terminate_from_main_die_in_thread_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    UNITTEST_HAS_CUSTOM_MAINLINE=True,
)

# Needs to be a different test -- It has to have direct control over the `main()` entry point.
env.CppUnitTest(
    target='set_terminate_from_thread_die_in_main_test',
    source=[
        'set_terminate_from_thread_die_in_main_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    UNITTEST_HAS_CUSTOM_MAINLINE=True,
)

# Needs to be a different test -- It has to have direct control over the `main()` entry point.
env.CppUnitTest(
    target='set_terminate_from_thread_die_in_thread_test',
    source=[
        'set_terminate_from_thread_die_in_thread_test.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    UNITTEST_HAS_CUSTOM_MAINLINE=True,
)

