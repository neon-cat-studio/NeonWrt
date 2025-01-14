# -*- mode: python; -*-

Import('env')
Import("get_option")
Import('http_client')
Import('ssl_provider')

env = env.Clone()

env.Library(
    target='network',
    source=[
        "cidr.cpp",
        "hostandport.cpp",
        "hostname_canonicalization.cpp",
        "sockaddr.cpp",
        "socket_exception.cpp",
        "socket_utils.cpp",
        env.Idlc('hostandport.idl')[0],
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/server_options_core',
        '$BUILD_DIR/mongo/util/concurrency/spin_lock',
        '$BUILD_DIR/mongo/util/winutil',
    ],
)

env.Library(
    target='ssl_options',
    source=[
        "ssl_options.cpp",
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/server_options_core',
        '$BUILD_DIR/mongo/util/options_parser/options_parser',
    ]
)

env.Library(
    target='ssl_options_client',
    source=[
        'ssl_options_client.cpp',
        env.Idlc('ssl_options_client.idl')[0],
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        'ssl_options',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/util/options_parser/options_parser',
    ]
)

env.Library(
    target='ssl_options_server',
    source=[
        'ssl_options_server.cpp',
        env.Idlc('ssl_options_server.idl')[0],
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        'ssl_options',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/db/server_options_core',
        '$BUILD_DIR/mongo/util/options_parser/options_parser',
    ]
)

env.Library(
    target='socket',
    source=[
        "sock.cpp",
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/util/fail_point',
        'network',
    ]
)

env.Library(
    target='ssl_types',
    source=[
        "ssl_types.cpp",
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
    LIBDEPS_PRIVATE=[
        '$BUILD_DIR/mongo/transport/transport_layer_common',
        'ssl_options',
    ]
)

if not get_option('ssl') == 'off':
    if ssl_provider == 'openssl':
        env.Library(
            target='openssl_init',
            source=[
                'openssl_init.cpp',
            ],
            LIBDEPS=[
                '$BUILD_DIR/mongo/base',
                'ssl_options',
            ],
        );

    env.Library(
        target='ssl_manager',
        source=[
            "private/ssl_expiration.cpp",
            "ssl_manager.cpp",
            "ssl_parameters.cpp",
            "ssl_manager_%s.cpp" % (ssl_provider),
            "ssl_stream.cpp",
            env.Idlc('ssl_parameters.idl')[0],
            "ocsp/ocsp_manager.cpp",
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/base',
            '$BUILD_DIR/mongo/db/auth/auth',
            '$BUILD_DIR/mongo/util/caching',
            '$BUILD_DIR/mongo/util/concurrency/thread_pool',
            '$BUILD_DIR/third_party/shim_asio',
            'network',
            'openssl_init' if ssl_provider == 'openssl' else '',
            'socket',
            'ssl_options',
            'ssl_types',
        ],
        LIBDEPS_PRIVATE=[
            '$BUILD_DIR/mongo/base/secure_allocator',
            '$BUILD_DIR/mongo/crypto/sha_block_${MONGO_CRYPTO}',
            '$BUILD_DIR/mongo/db/server_options_core',
            '$BUILD_DIR/mongo/db/service_context',
            '$BUILD_DIR/mongo/idl/server_parameter',
            '$BUILD_DIR/mongo/util/background_job',
            '$BUILD_DIR/mongo/util/icu',
            '$BUILD_DIR/mongo/util/winutil',
            'http_client',
        ],
    )

    env.Library(
        target='ssl_parameters_auth',
        source=[
            'ssl_parameters_auth.cpp',
            env.Idlc('ssl_parameters_auth.idl')[0],
        ],
        LIBDEPS_PRIVATE=[
            'ssl_options',
            '$BUILD_DIR/mongo/client/authentication',
            '$BUILD_DIR/mongo/db/server_options_core',
            '$BUILD_DIR/mongo/idl/server_parameter',
        ],
    )
else:
    env.Library(
        target='ssl_manager',
        source=[
            "ssl_manager_none.cpp",
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/base',
            'ssl_options',
        ],
    )

    env.Library(
        target='ssl_parameters_auth',
        source=[
            "ssl_parameters_auth_none.cpp",
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/base',
        ],
    )

if http_client == "off":
    env.Library(
        target='http_client',
        source=[
            'http_client_none.cpp',
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/base',
        ],
    )
else:
    env.Library(
        target='http_client',
        source=[
            'http_client_curl.cpp',
        ],
        LIBDEPS=[
            '$BUILD_DIR/mongo/base',
        ],
        SYSLIBDEPS=[
            'curl',
        ],
    )

env.CppUnitTest(
    target='util_net_test',
    source=[
        'cidr_test.cpp',
        'hostandport_test.cpp',
    ],
    LIBDEPS=[
        'network',
    ],
)

env.CppLibfuzzerTest(
    target='asn1_parser_fuzzer',
    source=[
        'asn1_parser_fuzzer.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/util/net/ssl_manager',
    ],
)

if get_option('ssl') == 'on':
    env.CppUnitTest(
        target='util_net_ssl_test',
        source=[
            'ssl_manager_test.cpp',
            'ssl_options_test.cpp',
            'sock_test.cpp',
        ],
        LIBDEPS=[
            'network',
            'socket',
            'ssl_manager',
            'ssl_options_server',
            '$BUILD_DIR/mongo/db/server_options_servers',
            '$BUILD_DIR/mongo/util/cmdline_utils/cmdline_utils',
            '$BUILD_DIR/mongo/util/fail_point',
        ],
    )

