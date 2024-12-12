# -*- mode: python -*-

Import([
    "get_option",
    "env",
    ])

env = env.Clone()
env.InjectThirdPartyIncludePaths(libraries=['zlib'])

def removeIfPresent(lst, item):
    try:
        lst.remove(item)
    except ValueError:
        pass

for to_remove in ['-Werror', '-Wall', '-W', '/W3']:
    removeIfPresent(env['CCFLAGS'], to_remove)

# See what -D's show up in make.  The AB_CD one might change, but we're little
# endian only for now so I think it's sane
env.Prepend(CPPDEFINES=[
        'IMPL_MFBT',
        'JS_USE_CUSTOM_ALLOCATOR',
        'STATIC_JS_API=1',
        'U_NO_DEFAULT_INCLUDE_UTF_HEADERS=1',
        ])

if get_option('spider-monkey-dbg') == "on":
    env.Prepend(CPPDEFINES=[
            'DEBUG',
            'JS_DEBUG',
            'JS_GC_ZEAL',
            ])

env.Append(
    CCFLAGS=[
        '-include', 'js-confdefs.h',
        '-Wno-invalid-offsetof',
    ],
    CXXFLAGS=[
        '-Wno-non-virtual-dtor',
    ],
)

# js/src, js/public and mfbt are the only required sources right now, that
# could change in the future
#
# Also:
# We pre-generate configs for platforms and just check them in.  Running
# mozilla's config requires a relatively huge portion of their tree.
env.Prepend(CPPPATH=[
    'extract/js/src',
    'extract/mfbt',
    'extract/intl/icu/source/common',
    'include',
    'mongo_sources',
    'platform/' + env["TARGET_ARCH"] + "/" + env["TARGET_OS"] + "/build",
    'platform/' + env["TARGET_ARCH"] + "/" + env["TARGET_OS"] + "/include",
])

sources = [
    "extract/js/src/builtin/RegExp.cpp",
    "extract/js/src/frontend/Parser.cpp",
    "extract/js/src/jsarray.cpp",
    "extract/js/src/jsatom.cpp",
    "extract/js/src/jsmath.cpp",
    "extract/js/src/jsutil.cpp",
    "extract/js/src/gc/StoreBuffer.cpp",
    "extract/js/src/mfbt/Unified_cpp_mfbt0.cpp",
    "extract/js/src/perf/pm_stub.cpp",
    "extract/js/src/vm/Initialization.cpp",
    "extract/mfbt/Compression.cpp",
]


if env['TARGET_ARCH'] == 'x86_64':
    sources.extend([
        "extract/js/src/jit/x86-shared/Disassembler-x86-shared.cpp",
    ])

sources.extend(Glob('platform/' + env["TARGET_ARCH"] + "/" + env["TARGET_OS"] + "/build/*.cpp")),

# All of those unified sources come in from configure.  The files don't
# actually build individually anymore.
env.Library(
    target="mozjs",
    source=sources,
    LIBDEPS_TAGS=[
        # Depends on allocation symbols defined elsewhere
        'illegal_cyclic_or_unresolved_dependencies_whitelisted',
    ],
)
