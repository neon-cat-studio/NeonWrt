# -*- mode: python -*-

Import("env")
Import("has_option")
Import("debugBuild")

files = [
    'src/base/dynamic_annotations.c',
    'src/base/spinlock_internal.cc',
    'src/base/logging.cc',
    'src/base/atomicops-internals-x86.cc',
    'src/base/sysinfo.cc',
    'src/base/spinlock.cc',
    'src/base/vdso_support.cc',
    'src/base/elf_mem_image.cc',
    'src/malloc_hook.cc',
    'src/span.cc',
    'src/internal_logging.cc',
    'src/symbolize.cc',
    'src/memfs_malloc.cc',
    'src/central_freelist.cc',
    'src/thread_cache.cc',
    'src/page_heap.cc',
    'src/common.cc',
    'src/static_vars.cc',
    'src/stack_trace_table.cc',
    'src/malloc_extension.cc',
    'src/sampler.cc',
    'src/stacktrace.cc'
    ]

files += [
    'src/maybe_threads.cc',
    'src/system-alloc.cc',
    ]

if not debugBuild:
    files += ['src/tcmalloc.cc'],
else:
    files += ['src/debugallocation.cc']

if has_option( 'use-cpu-profiler' ):
    files += [
        'src/profiler.cc',
        'src/profiledata.cc',
        'src/profile-handler.cc'
        ]

__malloc_hook_fragment = '''
#include <malloc.h>
void* (* volatile __malloc_hook)(size_t, const void*) = 0;
'''

def __checkMallocHookVolatile(check_context):
    check_context.Message("Checking if __malloc_hook is declared volatile... ")
    is_malloc_hook_volatile = check_context.TryCompile(__malloc_hook_fragment, '.cc')
    check_context.Result(is_malloc_hook_volatile)
    malloc_hook_define = 'MALLOC_HOOK_MAYBE_VOLATILE='
    if is_malloc_hook_volatile:
        malloc_hook_define += 'volatile'
    check_context.env.Append(CPPDEFINES=[malloc_hook_define])


conf = Configure(env.Clone(), custom_tests=dict(CheckMallocHookVolatile=__checkMallocHookVolatile))
conf.CheckMallocHookVolatile()
env = conf.Finish()


env.Append( CPPDEFINES=[ "NO_TCMALLOC_SAMPLES", "NO_HEAP_CHECK"] )

# The build system doesn't define NDEBUG globally for historical reasons, however, TCMalloc
# expects that NDEBUG is used to select between preferring the mmap or the sbrk allocator. For
# non-debug builds, we want to prefer the sbrk allocator since this is TCMallocs preferred
# production deployment configuration. See the use of NDEBUG and kDebugMode in
# src/system-alloc.cc for more details.
if not debugBuild:
    env.Append( CPPDEFINES=["NDEBUG"] )

env.Prepend( CPPPATH=["src/"] )

my_SYSLIBDEPS = []

if has_option( 'use-cpu-profiler' ):
    env.Append( CPPDEFINES=["NO_FRAME_POINTER", ("HAVE_LIBUNWIND_H", "1")] )
    my_SYSLIBDEPS.append( "unwind" )

def removeIfPresent(lst, item):
    try:
        lst.remove(item)
    except ValueError:
        pass

for to_remove in ['-Werror', "-Wsign-compare","-Wall"]:
    removeIfPresent(env['CCFLAGS'], to_remove)

env.Library('tcmalloc_minimal', files, SYSLIBDEPS=my_SYSLIBDEPS)
