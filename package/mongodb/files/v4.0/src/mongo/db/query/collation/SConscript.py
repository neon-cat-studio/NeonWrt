# -*- mode: python -*-

Import("env")

env = env.Clone()

env.Library(
    target="collator_interface",
    source=[
        "collation_index_key.cpp",
        "collation_spec.cpp",
        "collator_interface.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
    ],
)

env.CppUnitTest(
    target="collation_spec_test",
    source=[
        "collation_spec_test.cpp",
    ],
    LIBDEPS=[
        "collator_interface",
    ],
)

env.Library(
    target="collator_interface_mock",
    source=[
        "collator_interface_mock.cpp",
    ],
    LIBDEPS=[
        "collator_interface",
    ],
)

env.CppUnitTest(
    target="collator_interface_mock_test",
    source=[
        "collator_interface_mock_test.cpp",
    ],
    LIBDEPS=[
        "collator_interface_mock",
    ],
)

env.CppUnitTest(
    target="collation_bson_comparison_test",
    source=[
        "collation_bson_comparison_test.cpp",
    ],
    LIBDEPS=[
        "collator_interface_mock",
    ],
)

env.CppUnitTest(
    target="collation_index_key_test",
    source=[
        "collation_index_key_test.cpp",
    ],
    LIBDEPS=[
        "collator_interface",
        "collator_interface_mock",
    ],
)

env.Library(
    target="collator_factory_interface",
    source=[
        "collator_factory_interface.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/db/service_context",
        "collator_interface",
    ],
)

env.Library(
    target="collator_factory_mock",
    source=[
        "collator_factory_mock.cpp",
    ],
    LIBDEPS=[
        "collator_factory_interface",
        "collator_interface_mock",
    ],
)

env.CppUnitTest(
    target="collator_factory_mock_test",
    source=[
        "collator_factory_mock_test.cpp",
    ],
    LIBDEPS=[
        "collator_factory_mock",
    ],
)

env.CppUnitTest(
    target="collator_factory_icu_test",
    source=[
        "collator_factory_icu_locales_test.cpp",
        "collator_factory_icu_test.cpp",
    ],
    LIBDEPS=[
        "collator_icu",
    ],
)

# The collator_icu library and the collator_interface_icu_test unit tests need an environment which
# has access to the third-party ICU headers.
icuEnv = env.Clone()

icuEnv.Library(
    target="collator_icu",
    source=[
        "collator_factory_icu.cpp",
        "collator_interface_icu.cpp",
    ],
    LIBDEPS=[
        "$BUILD_DIR/mongo/base",
        "$BUILD_DIR/mongo/bson/util/bson_extract",
        "$BUILD_DIR/mongo/util/icu_init",
        "$BUILD_DIR/third_party/shim_icu",
        "collator_factory_interface",
    ],
)

icuEnv.CppUnitTest(
    target="collator_interface_icu_test",
    source=[
        "collator_interface_icu_test.cpp",
    ],
    LIBDEPS=[
        "collator_icu",
    ],
)
