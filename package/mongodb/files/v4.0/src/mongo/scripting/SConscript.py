# -*- mode: python -*-

import libdeps

Import([
    'env',
    'get_option',
    'serverJs',
    'usemozjs',
])

env.Library(
    target='scripting_common',
    source=[
        'deadline_monitor.cpp',
        'dbdirectclient_factory.cpp',
        'engine.cpp',
        'utils.cpp',
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/mongo/client/clientdriver_network',
        '$BUILD_DIR/mongo/shell/mongojs',
        '$BUILD_DIR/mongo/util/md5',
    ],
)

env.Library(
    target='bson_template_evaluator',
    source=[
        "bson_template_evaluator.cpp",
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
    ],
)

env.CppUnitTest(
    target='bson_template_evaluator_test',
    source=[
        'bson_template_evaluator_test.cpp',
    ],
    LIBDEPS=[
        'bson_template_evaluator',
    ],
)

env.Library(
    target='scripting_none',
    source=[
        'engine_none.cpp',
    ],
    LIBDEPS=[
        'bson_template_evaluator',
        'scripting_common',
    ],
)

if usemozjs:
    scriptingEnv = env.Clone()
    scriptingEnv.InjectThirdPartyIncludePaths(libraries=['mozjs'])

    # TODO: get rid of all of this /FI and -include stuff and migrate to a shim
    # header we include in all of our files.
    scriptingEnv.Append(
        CCFLAGS=[
            '-include', 'js-config.h',
            '-include', 'js/RequiredDefines.h',
            '-Wno-invalid-offsetof',
        ],
        CXXFLAGS=[
            '-Wno-non-virtual-dtor',
        ],
    )

    scriptingEnv.Prepend(CPPDEFINES=[
        'JS_USE_CUSTOM_ALLOCATOR',
        'STATIC_JS_API=1',
    ])

    if get_option('spider-monkey-dbg') == "on":
        scriptingEnv.Prepend(CPPDEFINES=[
            'DEBUG',
            'JS_DEBUG',
        ])

    scriptingEnv.JSHeader(
        target='mozjs/mongohelpers_js.cpp',
        source=[
            'mozjs/mongohelpers.js'
        ]
    )

    env.Alias('generated-sources', 'mozjs/mongohelpers_js.cpp')

    scriptingEnv.Library(
        target='scripting',
        source=[
            'mozjs/base.cpp',
            'mozjs/bindata.cpp',
            'mozjs/bson.cpp',
            'mozjs/code.cpp',
            'mozjs/countdownlatch.cpp',
            'mozjs/cursor.cpp',
            'mozjs/cursor_handle.cpp',
            'mozjs/db.cpp',
            'mozjs/dbcollection.cpp',
            'mozjs/dbpointer.cpp',
            'mozjs/dbquery.cpp',
            'mozjs/dbref.cpp',
            'mozjs/engine.cpp',
            'mozjs/error.cpp',
            'mozjs/exception.cpp',
            'mozjs/global.cpp',
            'mozjs/idwrapper.cpp',
            'mozjs/implscope.cpp',
            'mozjs/internedstring.cpp',
            'mozjs/jscustomallocator.cpp',
            'mozjs/jsstringwrapper.cpp',
            'mozjs/jsthread.cpp',
            'mozjs/maxkey.cpp',
            'mozjs/minkey.cpp',
            'mozjs/mongo.cpp',
            'mozjs/mongohelpers.cpp',
            'mozjs/mongohelpers_js.cpp',
            'mozjs/nativefunction.cpp',
            'mozjs/numberdecimal.cpp',
            'mozjs/numberint.cpp',
            'mozjs/numberlong.cpp',
            'mozjs/object.cpp',
            'mozjs/objectwrapper.cpp',
            'mozjs/oid.cpp',
            'mozjs/PosixNSPR.cpp',
            'mozjs/proxyscope.cpp',
            'mozjs/regexp.cpp',
            'mozjs/session.cpp',
            'mozjs/status.cpp',
            'mozjs/timestamp.cpp',
            'mozjs/uri.cpp',
            'mozjs/valuereader.cpp',
            'mozjs/valuewriter.cpp',
            env.Idlc('mozjs/end_sessions.idl')[0],
        ],
        LIBDEPS=[
            'bson_template_evaluator',
            'scripting_common',
            '$BUILD_DIR/mongo/shell/mongojs',
            '$BUILD_DIR/mongo/db/service_context',
        ],
        LIBDEPS_PRIVATE=[
            '$BUILD_DIR/third_party/shim_mozjs',
        ],
    )
else:
    env.Library(
        target='scripting',
        source=[
            'scripting_none.cpp'
        ],
        LIBDEPS=[
            'scripting_none',
        ],
    )

env.Library(
    target='scripting_server',
    source=[
        'scripting_server.cpp',
    ],
    LIBDEPS=[
        'scripting' if serverJs else 'scripting_none',
    ],
)

env.CppUnitTest(
    target='deadline_monitor_test',
    source=[
        'deadline_monitor_test.cpp',
    ],
    LIBDEPS=[
        'scripting_common',
    ],
)
