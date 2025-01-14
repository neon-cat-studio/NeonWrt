# Copyright 2012 the V8 project authors. All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     * Neither the name of Google Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# set up path for js2c import
import sys
from os.path import join, dirname, abspath
root_dir = dirname(File('SConscript').rfile().abspath)
sys.path.insert(0, join(root_dir, 'tools'))
import js2c

Import("env debugBuild")

# pared-down copies of the equivalent structures in v8's SConstruct/SConscript:
LIBRARY_FLAGS = {
  'all': {
    'all': {
      'CPPDEFINES':   ['ENABLE_DEBUGGER_SUPPORT', 'VERIFY_HEAP'],
    },
    'mode:debug': {
      'CPPDEFINES':   ['V8_ENABLE_CHECKS', 'OBJECT_PRINT']
    },
  },
  'gcc': {
    'all': {
      'CCFLAGS':      ['-Wno-unused-parameter',
                       '-Woverloaded-virtual',
                       '-Wnon-virtual-dtor']
    },
    'mode:debug': {
      'CPPDEFINES':   ['ENABLE_DISASSEMBLER', 'DEBUG'],
    },
    'os:linux': {
      'CCFLAGS':      ['-ansi', '-pedantic'],
    },
    'arch:ia32': {
      'CPPDEFINES':   ['V8_TARGET_ARCH_IA32'],
    },
    'arch:x64': {
      'CPPDEFINES':   ['V8_TARGET_ARCH_X64'],
    },
    'arch:arm64': {
      'CPPDEFINES':   ['V8_TARGET_ARCH_ARM64'],
    },
    'arch:arm': {
      'CPPDEFINES':   ['V8_TARGET_ARCH_ARM'],
    },
    'arch:mips': {
      'CPPDEFINES':   ['V8_TARGET_ARCH_MIPS'],
    },
    'arch:mipsel': {
      'CPPDEFINES':   ['V8_TARGET_ARCH_MIPS'],
    }
  }
}

SOURCES = {
  'all': Split("""
    accessors.cc
    allocation.cc
    allocation-site-scopes.cc
    allocation-tracker.cc
    api.cc
    arguments.cc
    assembler.cc
    assert-scope.cc
    ast.cc
    atomicops_internals_x86_gcc.cc
    bignum-dtoa.cc
    bignum.cc
    bootstrapper.cc
    builtins.cc
    cached-powers.cc
    checks.cc
    code-stubs-hydrogen.cc
    code-stubs.cc
    codegen.cc
    compilation-cache.cc
    compiler.cc
    contexts.cc
    conversions.cc
    counters.cc
    cpu-profiler.cc
    cpu.cc
    data-flow.cc
    date.cc
    dateparser.cc
    debug-agent.cc
    debug.cc
    deoptimizer.cc
    disassembler.cc
    diy-fp.cc
    dtoa.cc
    elements-kind.cc
    elements.cc
    execution.cc
    extensions/externalize-string-extension.cc
    extensions/free-buffer-extension.cc
    extensions/gc-extension.cc
    extensions/statistics-extension.cc
    extensions/trigger-failure-extension.cc
    factory.cc
    fast-dtoa.cc
    fixed-dtoa.cc
    flags.cc
    frames.cc
    full-codegen.cc
    func-name-inferrer.cc
    gdb-jit.cc
    global-handles.cc
    handles.cc
    heap-profiler.cc
    heap-snapshot-generator.cc
    heap.cc
    hydrogen-bce.cc
    hydrogen-bch.cc
    hydrogen-canonicalize.cc
    hydrogen-check-elimination.cc
    hydrogen-dce.cc
    hydrogen-dehoist.cc
    hydrogen-environment-liveness.cc
    hydrogen-escape-analysis.cc
    hydrogen-gvn.cc
    hydrogen-infer-representation.cc
    hydrogen-infer-types.cc
    hydrogen-instructions.cc
    hydrogen-load-elimination.cc
    hydrogen-mark-deoptimize.cc
    hydrogen-mark-unreachable.cc
    hydrogen-osr.cc
    hydrogen-range-analysis.cc
    hydrogen-redundant-phi.cc
    hydrogen-removable-simulates.cc
    hydrogen-representation-changes.cc
    hydrogen-sce.cc
    hydrogen-store-elimination.cc
    hydrogen-uint32-analysis.cc
    hydrogen.cc
    ic.cc
    icu_util.cc
    incremental-marking.cc
    interface.cc
    interpreter-irregexp.cc
    isolate.cc
    jsregexp.cc
    lithium-allocator.cc
    lithium-codegen.cc
    lithium.cc
    liveedit.cc
    log-utils.cc
    log.cc
    mark-compact.cc
    messages.cc
    objects-printer.cc
    objects-visiting.cc
    objects.cc
    objects-debug.cc
    once.cc
    optimizing-compiler-thread.cc
    parser.cc
    preparse-data.cc
    preparser.cc
    profile-generator.cc
    property.cc
    regexp-macro-assembler-irregexp.cc
    regexp-macro-assembler.cc
    regexp-stack.cc
    rewriter.cc
    runtime-profiler.cc
    runtime.cc
    safepoint-table.cc
    sampler.cc
    scanner-character-streams.cc
    scanner.cc
    scopeinfo.cc
    scopes.cc
    serialize.cc
    snapshot-common.cc
    spaces.cc
    store-buffer.cc
    string-search.cc
    string-stream.cc
    strtod.cc
    stub-cache.cc
    sweeper-thread.cc
    token.cc
    transitions.cc
    trig-table.cc
    type-info.cc
    types.cc
    typing.cc
    unicode.cc
    utils.cc
    v8-counters.cc
    v8.cc
    v8conversions.cc
    v8threads.cc
    v8utils.cc
    variables.cc
    version.cc
    zone.cc
    platform/condition-variable.cc
    platform/mutex.cc
    platform/semaphore.cc
    platform/socket.cc
    platform/time.cc
    utils/random-number-generator.cc
    """),
  'arch:ia32': Split("""
    ia32/assembler-ia32.cc
    ia32/builtins-ia32.cc
    ia32/code-stubs-ia32.cc
    ia32/codegen-ia32.cc
    ia32/cpu-ia32.cc
    ia32/debug-ia32.cc
    ia32/deoptimizer-ia32.cc
    ia32/disasm-ia32.cc
    ia32/frames-ia32.cc
    ia32/full-codegen-ia32.cc
    ia32/ic-ia32.cc
    ia32/lithium-codegen-ia32.cc
    ia32/lithium-gap-resolver-ia32.cc
    ia32/lithium-ia32.cc
    ia32/macro-assembler-ia32.cc
    ia32/regexp-macro-assembler-ia32.cc
    ia32/stub-cache-ia32.cc
    """),
  'arch:x64': Split("""
    x64/assembler-x64.cc
    x64/builtins-x64.cc
    x64/code-stubs-x64.cc
    x64/codegen-x64.cc
    x64/cpu-x64.cc
    x64/debug-x64.cc
    x64/deoptimizer-x64.cc
    x64/disasm-x64.cc
    x64/frames-x64.cc
    x64/full-codegen-x64.cc
    x64/ic-x64.cc
    x64/lithium-codegen-x64.cc
    x64/lithium-gap-resolver-x64.cc
    x64/lithium-x64.cc
    x64/macro-assembler-x64.cc
    x64/regexp-macro-assembler-x64.cc
    x64/stub-cache-x64.cc
    """),
  'arch:arm64': Split("""
    arm64/assembler-arm64.cc
    arm64/builtins-arm64.cc
    arm64/code-stubs-arm64.cc
    arm64/codegen-arm64.cc
    arm64/cpu-arm64.cc
    arm64/debug-arm64.cc
    arm64/decoder-arm64.cc
    arm64/deoptimizer-arm64.cc
    arm64/disasm-arm64.cc
    arm64/frames-arm64.cc
    arm64/full-codegen-arm64.cc
    arm64/ic-arm64.cc
    arm64/instructions-arm64.cc
    arm64/instrument-arm64.cc
    arm64/lithium-arm64.cc
    arm64/lithium-codegen-arm64.cc
    arm64/lithium-gap-resolver-arm64.cc
    arm64/macro-assembler-arm64.cc
    arm64/regexp-macro-assembler-arm64.cc
    arm64/stub-cache-arm64.cc
    arm64/utils-arm64.cc
    """),
  'arch:arm': Split("""
    arm/assembler-arm.cc
    arm/builtins-arm.cc
    arm/code-stubs-arm.cc
    arm/codegen-arm.cc
    arm/constants-arm.cc
    arm/cpu-arm.cc
    arm/debug-arm.cc
    arm/deoptimizer-arm.cc
    arm/disasm-arm.cc
    arm/frames-arm.cc
    arm/full-codegen-arm.cc
    arm/ic-arm.cc
    arm/lithium-arm.cc
    arm/lithium-codegen-arm.cc
    arm/lithium-gap-resolver-arm.cc
    arm/macro-assembler-arm.cc
    arm/regexp-macro-assembler-arm.cc
    arm/simulator-arm.cc
    arm/stub-cache-arm.cc
    """),
  'arch:mips': Split("""
    mips/assembler-mips.cc
    mips/builtins-mips.cc
    mips/code-stubs-mips.cc
    mips/codegen-mips.cc
    mips/constants-mips.cc
    mips/cpu-mips.cc
    mips/debug-mips.cc
    mips/deoptimizer-mips.cc
    mips/disasm-mips.cc
    mips/frames-mips.cc
    mips/full-codegen-mips.cc
    mips/ic-mips.cc
    mips/lithium-mips.cc
    mips/lithium-codegen-mips.cc
    mips/lithium-gap-resolver-mips.cc
    mips/macro-assembler-mips.cc
    mips/regexp-macro-assembler-mips.cc
    mips/simulator-mips.cc
    mips/stub-cache-mips.cc
    """),
  'arch:mipsel': Split("""
    mips/assembler-mips.cc
    mips/builtins-mips.cc
    mips/code-stubs-mips.cc
    mips/codegen-mips.cc
    mips/constants-mips.cc
    mips/cpu-mips.cc
    mips/debug-mips.cc
    mips/deoptimizer-mips.cc
    mips/disasm-mips.cc
    mips/frames-mips.cc
    mips/full-codegen-mips.cc
    mips/ic-mips.cc
    mips/lithium-mips.cc
    mips/lithium-codegen-mips.cc
    mips/lithium-gap-resolver-mips.cc
    mips/macro-assembler-mips.cc
    mips/regexp-macro-assembler-mips.cc
    mips/simulator-mips.cc
    mips/stub-cache-mips.cc
    """),
  'os:linux':   ['platform-linux.cc', 'platform-posix.cc'],
  'mode:release': [],
  'mode:debug': [
    'prettyprinter.cc', 'regexp-macro-assembler-tracer.cc'
  ]
}

EXPERIMENTAL_LIBRARY_FILES = '''
proxy.js
collection.js
'''.split()

LIBRARY_FILES = '''
runtime.js
v8natives.js
array.js
string.js
uri.js
math.js
messages.js
apinatives.js
date.js
regexp.js
json.js
liveedit-debugger.js
mirror-debugger.js
debug-debugger.js
'''.split()

def get_flags(flag, toolchain, options):
    ret = []
    for t in (toolchain, 'all'):
        for o in (options.values() + ['all']):
            ret.extend(LIBRARY_FLAGS[t].get(o,{}).get(flag,[]))
    return ret

def get_options():
    processor = env['ARCH']
    if processor == 'i386':
        arch_string = 'arch:ia32'
    elif processor == 'i686':
        arch_string = 'arch:ia32'
    elif processor == 'x86_64':
        arch_string = 'arch:x64'
    elif processor == 'amd64':
        arch_string = 'arch:x64'
    elif processor == 'aarch64':
        arch_string = 'arch:arm64'
    elif processor == 'arm':
        arch_string = 'arch:arm'
    elif processor == 'armv7l':
        arch_string = 'arch:arm'
    elif processor == 'mips':
        arch_string = 'arch:mips'
    elif processor == 'mipsel':
        arch_string = 'arch:mipsel'
    else:
        assert False, "Unsupported architecture: " + processor

    os_string = 'os:linux'

    if debugBuild:
        mode_string = 'mode:debug'
    else:
        mode_string = 'mode:release'

    return {'mode': mode_string, 'os': os_string, 'arch': arch_string}

def get_sources(options):
    keys = options.values() + ['all']

    sources = []
    for i in keys:
        sources.extend(('src/'+s) for s in SOURCES[i])

    # sources generated from .js files:
    sources.append('src/libraries.cc')
    sources.append('src/experimental-libraries.cc')

    # we're building with v8 "snapshot=off", which requires this file:
    sources.append('src/snapshot-empty.cc')

    return sources

def get_toolchain():
    return 'gcc'

# convert our SConstruct variables to their v8 equivalents:
toolchain = get_toolchain()
options = get_options()
sources = get_sources(options)

env = env.Clone()

# remove -Iinclude and prepend -Isrc, to resolve namespace conflicts:
#
# mongo source needs to compile with include/v8.h, but v8 source
# needs to compile with src/v8.h
#
# in addition, v8 source needs to compile with src/parser.h, which
# Include/parser.h (v8 doesn't even use any of those header files)
env['CPPPATH'].remove('#/src/third_party/v8-3.25/include')
env.Prepend(CPPPATH='#/src/third_party/v8-3.25/src')

# add v8 ccflags and cppdefines to environment if they're not already
# present
ccflags = get_flags('CCFLAGS', toolchain, options)
ccflags = filter(lambda f :
                     f not in env['CCFLAGS'] + env['CXXFLAGS'] + env['CFLAGS'],
                 ccflags)
env.Append(CCFLAGS=ccflags)
cppdefines = get_flags('CPPDEFINES', toolchain, options)
cppdefines = filter(lambda f : f not in env['CPPDEFINES'], cppdefines)
env.Append(CPPDEFINES=cppdefines)

# NOTE: Suppress attempts to enable warnings in v8. Trying to individually suppress with -Wno-
# results in a game of whack-a-mole between various versions of clang and gcc as they add new
# warnings. We won't be changing the v8 sources, so the warnings aren't helpful.
def removeIfPresent(lst, item):
    try:
        lst.remove(item)
    except ValueError:
        pass

# NOTE: Along with the warning flags, remove any flags for LTO when building v8,
# as LTO builds currently appear to generate bad code with clang.
for to_remove in ['-Werror', '-Wall', '-W', "-flto"]:
    removeIfPresent(env['CCFLAGS'], to_remove)
    removeIfPresent(env['LINKFLAGS'], to_remove)

# specify rules for building libraries.cc and experimental-libraries.cc
env['BUILDERS']['JS2C'] = Builder(action=js2c.JS2C)
experimental_library_files = [('src/'+s) for s in EXPERIMENTAL_LIBRARY_FILES]
experimental_library_files.append('src/macros.py')
env.JS2C(['src/experimental-libraries.cc'],
         experimental_library_files,
         TYPE='EXPERIMENTAL',
         COMPRESSION='off')
library_files = [('src/'+s) for s in LIBRARY_FILES]
library_files.append('src/macros.py')
env.JS2C(['src/libraries.cc'], library_files, TYPE='CORE', COMPRESSION='off')

env.Library("v8", sources)