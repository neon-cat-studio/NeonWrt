# -*- mode: python; -*-
import atexit
import copy
import datetime
import errno
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import textwrap
import uuid
import multiprocessing

import SCons

# This must be first, even before EnsureSConsVersion, if
# we are to avoid bulk loading all tools in the DefaultEnvironment.
DefaultEnvironment(tools=[])

# These come from site_scons/mongo. Import these things
# after calling DefaultEnvironment, for the sake of paranoia.
import mongo
import mongo.platform as mongo_platform
import mongo.toolchain as mongo_toolchain
import mongo.generators as mongo_generators

EnsurePythonVersion(2, 7)
EnsureSConsVersion(2, 5)

from buildscripts import utils
from buildscripts import moduleconfig

import libdeps

atexit.register(mongo.print_build_failures)

def add_option(name, **kwargs):

    if 'dest' not in kwargs:
        kwargs['dest'] = name

    if 'metavar' not in kwargs and kwargs.get('type', None) == 'choice':
        kwargs['metavar'] = '[' + '|'.join(kwargs['choices']) + ']'

    AddOption('--' + name, **kwargs)

def get_option(name):
    return GetOption(name)

def has_option(name):
    optval = GetOption(name)
    # Options with nargs=0 are true when their value is the empty tuple. Otherwise,
    # if the value is falsish (empty string, None, etc.), coerce to False.
    return True if optval == () else bool(optval)

def make_variant_dir_generator():
    memoized_variant_dir = [False]
    def generate_variant_dir(target, source, env, for_signature):
        if not memoized_variant_dir[0]:
            memoized_variant_dir[0] = env.subst('$BUILD_ROOT/$VARIANT_DIR')
        return memoized_variant_dir[0]
    return generate_variant_dir


# Always randomize the build order to shake out missing edges, and to help the cache:
# http://scons.org/doc/production/HTML/scons-user/ch24s06.html
SetOption('random', 1)

# Options TODOs:
#
# - We should either alphabetize the entire list of options, or split them into logical groups
#   with clear boundaries, and then alphabetize the groups. There is no way in SCons though to
#   inform it of options groups.
#
# - Many of these options are currently only either present or absent. This is not good for
#   scripting the build invocation because it means you need to interpolate in the presence of
#   the whole option. It is better to make all options take an optional on/off or true/false
#   using the nargs='const' mechanism.
#

add_option('prefix',
    default='$BUILD_ROOT/install',
    help='installation prefix',
)

add_option('install-mode',
    choices=['legacy', 'hygienic'],
    default='legacy',
    help='select type of installation',
    nargs=1,
    type='choice',
)

add_option('nostrip',
    help='do not strip installed binaries',
    nargs=0,
)

add_option('build-dir',
    default='#build',
    help='build output directory',
)

add_option('release',
    help='release build',
    nargs=0,
)

add_option('lto',
    help='enable link time optimizations (experimental, except with MSVC)',
    nargs=0,
)

add_option('dynamic-windows',
    help='dynamically link on Windows',
    nargs=0,
)

add_option('endian',
    choices=['big', 'little', 'auto'],
    default='auto',
    help='endianness of target platform',
    nargs=1,
    type='choice',
)

add_option('disable-minimum-compiler-version-enforcement',
    help='allow use of unsupported older compilers (NEVER for production builds)',
    nargs=0,
)

add_option('ssl',
    help='Enable SSL',
    nargs=0
)

add_option('ssl-provider',
    choices=['auto', 'openssl', 'native'],
    default='auto',
    help='Select the SSL engine to use',
    nargs=1,
    type='choice',
)

add_option('mmapv1',
    choices=['auto', 'on', 'off'],
    const='on',
    default='auto',
    help='Enable MMapV1',
    nargs='?',
    type='choice',
)

add_option('wiredtiger',
    choices=['on', 'off'],
    const='on',
    default='on',
    help='Enable wiredtiger',
    nargs='?',
    type='choice',
)

add_option('mobile-se',
    choices=['on', 'off'],
    const='on',
    default='off',
    help='Enable Mobile Storage Engine',
    nargs='?',
    type='choice',
)

js_engine_choices = ['mozjs', 'none']
add_option('js-engine',
    choices=js_engine_choices,
    default=js_engine_choices[0],
    help='JavaScript scripting engine implementation',
    type='choice',
)

add_option('server-js',
    choices=['on', 'off'],
    default='on',
    help='Build mongod without JavaScript support',
    type='choice',
)

add_option('libc++',
    help='use libc++ (experimental, requires clang)',
    nargs=0,
)

add_option('use-glibcxx-debug',
    help='Enable the glibc++ debug implementations of the C++ standard libary',
    nargs=0,
)

add_option('noshell',
    help="don't build shell",
    nargs=0,
)

add_option('safeshell',
    help="don't let shell scripts run programs (still, don't run untrusted scripts)",
    nargs=0,
)

add_option('dbg',
    choices=['on', 'off'],
    const='on',
    default='off',
    help='Enable runtime debugging checks',
    nargs='?',
    type='choice',
)

add_option('separate-debug',
    choices=['on', 'off'],
    const='on',
    default='off',
    help='Produce separate debug files (only effective in --install-mode=hygienic)',
    nargs='?',
    type='choice',
)

add_option('spider-monkey-dbg',
    choices=['on', 'off'],
    const='on',
    default='off',
    help='Enable SpiderMonkey debug mode',
    nargs='?',
    type='choice',
)

add_option('opt',
    choices=['on', 'size', 'off'],
    const='on',
    help='Enable compile-time optimization',
    nargs='?',
    type='choice',
)

add_option('sanitize',
    help='enable selected sanitizers',
    metavar='san1,san2,...sanN',
)

add_option('llvm-symbolizer',
    default='llvm-symbolizer',
    help='name of (or path to) the LLVM symbolizer',
)

add_option('durableDefaultOn',
    help='have durable default to on',
    nargs=0,
)

add_option('allocator',
    choices=["auto", "system", "tcmalloc"],
    default="auto",
    help='allocator to use (use "auto" for best choice for current platform)',
    type='choice',
)

add_option('gdbserver',
    help='build in gdb server support',
    nargs=0,
)

add_option('gcov',
    help='compile with flags for gcov',
    nargs=0,
)

add_option('enable-free-mon',
    choices=["auto", "on", "off"],
    default="auto",
    help='Disable support for Free Monitoring to avoid HTTP client library dependencies',
    type='choice',
)

add_option('use-sasl-client',
    help='Support SASL authentication in the client library',
    nargs=0,
)

add_option('use-system-mongo-c',
    choices=['on', 'off', 'auto'],
    const='on',
    default="auto",
    help="use system version of the mongo-c-driver (auto will use it if it's found)",
    nargs='?',
    type='choice',
)

add_option('use-new-tools',
    help='put new tools in the tarball',
    nargs=0,
)

add_option('build-mongoreplay',
    help='when building with --use-new-tools, build mongoreplay ( requires pcap dev )',
    nargs=1,
)

add_option('use-cpu-profiler',
    help='Link against the google-perftools profiler library',
    nargs=0,
)

add_option('build-fast-and-loose',
    choices=['on', 'off', 'auto'],
    const='on',
    default='auto',
    help='looser dependency checking',
    nargs='?',
    type='choice',
)

add_option('disable-warnings-as-errors',
    help="Don't add -Werror to compiler command line",
    nargs=0,
)

add_option('detect-odr-violations',
    help="Have the linker try to detect ODR violations, if supported",
    nargs=0,
)

add_option('variables-help',
    help='Print the help text for SCons variables',
    nargs=0,
)

add_option('cache',
    choices=["all", "nolinked"],
    const='all',
    help='Use an object cache rather than a per-build variant directory (experimental)',
    nargs='?',
)

add_option('cache-dir',
    default='$BUILD_ROOT/scons/cache',
    help='Specify the directory to use for caching objects if --cache is in use',
)

add_option("cxx-std",
    choices=["14"],
    default="14",
    help="Select the C++ langauge standard to build with",
)

def find_mongo_custom_variables():
    files = []
    for path in sys.path:
        probe = os.path.join(path, 'mongo_custom_variables.py')
        if os.path.isfile(probe):
            files.append(probe)
    return files

add_option('variables-files',
    default=find_mongo_custom_variables(),
    help="Specify variables files to load",
)

link_model_choices = ['auto', 'object', 'static', 'dynamic', 'dynamic-strict', 'dynamic-sdk']
add_option('link-model',
    choices=link_model_choices,
    default='auto',
    help='Select the linking model for the project',
    type='choice'
)

add_option('modules',
    help="Comma-separated list of modules to build. Empty means none. Default is all.",
)

add_option('runtime-hardening',
    choices=["on", "off"],
    default="on",
    help="Enable runtime hardening features (e.g. stack smash protection)",
    type='choice',
)

add_option('use-s390x-crc32',
    choices=["on", "off"],
    default="on",
    help="Enable CRC32 hardware accelaration on s390x",
    type='choice',
)

add_option('git-decider',
    choices=["on", "off"],
    const='on',
    default="off",
    help="Use git metadata for out-of-date detection for source files",
    nargs='?',
    type="choice",
)

add_option('jlink',
        help="Limit link concurrency to given value",
        const=0.5,
        default=None,
        nargs='?',
        type=float)

try:
    with open("version.json", "r") as version_fp:
        version_data = json.load(version_fp)

    if 'version' not in version_data:
        print("version.json does not contain a version string")
        Exit(1)
    if 'githash' not in version_data:
        version_data['githash'] = utils.get_git_version()

except IOError as e:
    # If the file error wasn't because the file is missing, error out
    if e.errno != errno.ENOENT:
        print("Error opening version.json: {0}".format(e.strerror))
        Exit(1)

    version_data = {
        'version': utils.get_git_describe()[1:],
        'githash': utils.get_git_version(),
    }

except ValueError as e:
    print("Error decoding version.json: {0}".format(e))
    Exit(1)

# Setup the command-line variables
def variable_shlex_converter(val):
    # If the argument is something other than a string, propogate
    # it literally.
    if not isinstance(val, basestring):
        return val
    return shlex.split(val, posix=True)

def variable_arch_converter(val):
    arches = {
        'x86_64': 'x86_64',
        'amd64':  'x86_64',
        'emt64':   'x86_64',
        'x86':    'i386',
    }
    val = val.lower()

    if val in arches:
        return arches[val]

    # Uname returns a bunch of possible x86's on Linux.
    # Check whether the value is an i[3456]86 processor.
    if re.match(r'^i[3-6]86$', val):
        return 'i386'

    # Return whatever val is passed in - hopefully it's legit
    return val

# The Scons 'default' tool enables a lot of tools that we don't actually need to enable.
# On platforms like Solaris, it actually does the wrong thing by enabling the sunstudio
# toolchain first. As such it is simpler and more efficient to manually load the precise
# set of tools we need for each platform.
# If we aren't on a platform where we know the minimal set of tools, we fall back to loading
# the 'default' tool.
def decide_platform_tools():
    return ['gcc', 'g++', 'gnulink', 'ar', 'gas']

def variable_tools_converter(val):
    tool_list = shlex.split(val)
    return tool_list + [
        "distsrc",
        "gziptool",
        'idl_tool',
        "jsheader",
        "mongo_benchmark",
        "mongo_integrationtest",
        "mongo_unittest",
        "textfile",
    ]

def variable_distsrc_converter(val):
    if not val.endswith("/"):
        return val + "/"
    return val

variables_files = variable_shlex_converter(get_option('variables-files'))
for file in variables_files:
    print("Using variable customization file %s" % file)

env_vars = Variables(
    files=variables_files,
    args=ARGUMENTS
)

sconsflags = os.environ.get('SCONSFLAGS', None)
if sconsflags:
    print("Using SCONSFLAGS environment variable arguments: %s" % sconsflags)

env_vars.Add('ABIDW',
    help="Configures the path to the 'abidw' (a libabigail) utility")

env_vars.Add('AR',
    help='Sets path for the archiver')

env_vars.Add('ARFLAGS',
    help='Sets flags for the archiver',
    converter=variable_shlex_converter)

env_vars.Add(
    'CACHE_SIZE',
    help='Maximum size of the cache (in gigabytes)',
    default=32,
    converter=lambda x:int(x)
)

env_vars.Add(
    'CACHE_PRUNE_TARGET',
    help='Maximum percent in-use in cache after pruning',
    default=66,
    converter=lambda x:int(x)
)

env_vars.Add('CC',
    help='Select the C compiler to use')

env_vars.Add('CCFLAGS',
    help='Sets flags for the C and C++ compiler',
    converter=variable_shlex_converter)

env_vars.Add('CFLAGS',
    help='Sets flags for the C compiler',
    converter=variable_shlex_converter)

env_vars.Add('CPPDEFINES',
    help='Sets pre-processor definitions for C and C++',
    converter=variable_shlex_converter,
    default=[])

env_vars.Add('CPPPATH',
    help='Adds paths to the preprocessor search path',
    converter=variable_shlex_converter)

env_vars.Add('CXX',
    help='Select the C++ compiler to use')

env_vars.Add('CXXFLAGS',
    help='Sets flags for the C++ compiler',
    converter=variable_shlex_converter)

# Note: This probably is only really meaningful when configured via a variables file. It will
# also override whatever the SCons platform defaults would be.
env_vars.Add('ENV',
    help='Sets the environment for subprocesses')

env_vars.Add('FRAMEWORKPATH',
    help='Adds paths to the linker search path for darwin frameworks',
    converter=variable_shlex_converter)

env_vars.Add('FRAMEWORKS',
    help='Adds extra darwin frameworks to link against',
    converter=variable_shlex_converter)

env_vars.Add('HOST_ARCH',
    help='Sets the native architecture of the compiler',
    converter=variable_arch_converter,
    default=None)

env_vars.Add('ICECC',
    help='Tell SCons where icecream icecc tool is')

env_vars.Add('ICERUN',
    help='Tell SCons where icecream icerun tool is')

env_vars.Add('ICECC_CREATE_ENV',
    help='Tell SCons where icecc-create-env tool is',
    default='buildscripts/icecc_create_env')

env_vars.Add('ICECC_SCHEDULER',
    help='Tell ICECC where the sceduler daemon is running')

env_vars.Add('LIBPATH',
    help='Adds paths to the linker search path',
    converter=variable_shlex_converter)

env_vars.Add('LIBS',
    help='Adds extra libraries to link against',
    converter=variable_shlex_converter)

env_vars.Add('LINKFLAGS',
    help='Sets flags for the linker',
    converter=variable_shlex_converter)

env_vars.Add('MAXLINELENGTH',
    help='Maximum line length before using temp files',
    # This is very small, but appears to be the least upper bound
    # across our platforms.
    #
    # See https://support.microsoft.com/en-us/help/830473/command-prompt-cmd.-exe-command-line-string-limitation
    default=4095)

# Note: This is only really meaningful when configured via a variables file. See the
# default_buildinfo_environment_data() function for examples of how to use this.
env_vars.Add('MONGO_BUILDINFO_ENVIRONMENT_DATA',
    help='Sets the info returned from the buildInfo command and --version command-line flag',
    default=mongo_generators.default_buildinfo_environment_data())

# Exposed to be able to cross compile Android/*nix from Windows without ending up with the .exe suffix.
env_vars.Add('PROGSUFFIX',
    help='Sets the suffix for built executable files')

env_vars.Add('MONGO_DIST_SRC_PREFIX',
    help='Sets the prefix for files in the source distribution archive',
    converter=variable_distsrc_converter,
    default="mongodb-src-r${MONGO_VERSION}")

env_vars.Add('MONGO_DISTARCH',
    help='Adds a string representing the target processor architecture to the dist archive',
    default='$TARGET_ARCH')

env_vars.Add('MONGO_DISTMOD',
    help='Adds a string that will be embedded in the dist archive naming',
    default='')

env_vars.Add('MONGO_DISTNAME',
    help='Sets the version string to be used in dist archive naming',
    default='$MONGO_VERSION')

def validate_mongo_version(key, val, env):
    regex = r'^(\d+)\.(\d+)\.(\d+)-?((?:(rc)(\d+))?.*)?'
    if not re.match(regex, val):
        print("Invalid MONGO_VERSION '{}', or could not derive from version.json or git metadata. Please add a conforming MONGO_VERSION=x.y.z[-extra] as an argument to SCons".format(val))
        Exit(1)

env_vars.Add('MONGO_VERSION',
    help='Sets the version string for MongoDB',
    default=version_data['version'],
    validator=validate_mongo_version)

env_vars.Add('MONGO_GIT_HASH',
    help='Sets the githash to store in the MongoDB version information',
    default=version_data['githash'])

env_vars.Add('OBJCOPY',
    help='Sets the path to objcopy',
    default=WhereIs('objcopy'))

env_vars.Add('RPATH',
    help='Set the RPATH for dynamic libraries and executables',
    converter=variable_shlex_converter)

env_vars.Add('SHCCFLAGS',
    help='Sets flags for the C and C++ compiler when building shared libraries',
    converter=variable_shlex_converter)

env_vars.Add('SHCFLAGS',
    help='Sets flags for the C compiler when building shared libraries',
    converter=variable_shlex_converter)

env_vars.Add('SHCXXFLAGS',
    help='Sets flags for the C++ compiler when building shared libraries',
    converter=variable_shlex_converter)

env_vars.Add('SHELL',
    help='Pick the shell to use when spawning commands')

env_vars.Add('SHLINKFLAGS',
    help='Sets flags for the linker when building shared libraries',
    converter=variable_shlex_converter)

env_vars.Add('TARGET_ARCH',
    help='Sets the architecture to build for',
    converter=variable_arch_converter,
    default=None)

env_vars.Add('TARGET_OS',
    help='Sets the target OS to build for',
    default=mongo_platform.get_running_os_name())

env_vars.Add('TOOLS',
    help='Sets the list of SCons tools to add to the environment',
    converter=variable_tools_converter,
    default=decide_platform_tools())

env_vars.Add('VARIANT_DIR',
    help='Sets the name (or generator function) for the variant directory',
    default=mongo_generators.default_variant_dir_generator,
)

env_vars.Add('VERBOSE',
    help='Control build verbosity (auto, on/off true/false 1/0)',
    default='auto',
)

env_vars.Add('STAGING_DIR',
    help='OpenWrt toolchain staging directory',
    default='./')

# -- Validate user provided options --

# A dummy environment that should *only* have the variables we have set. In practice it has
# some other things because SCons isn't quite perfect about keeping variable initialization
# scoped to Tools, but it should be good enough to do validation on any Variable values that
# came from the command line or from loaded files.
variables_only_env = Environment(
    # Disable platform specific variable injection
    platform=(lambda x: ()),
    # But do *not* load any tools, since those might actually set variables. Note that this
    # causes the value of our TOOLS variable to have no effect.
    tools=[],
    # Use the Variables specified above.
    variables=env_vars,
)

# don't run configure if user calls --help
if GetOption('help'):
    try:
        Help('\nThe following variables may also be set like scons VARIABLE=value\n', append=True)
        Help(env_vars.GenerateHelpText(variables_only_env), append=True)
    except TypeError:
        # The append=true kwarg is only supported in scons>=2.4. Without it, calls to Help() clobber
        # the automatically generated options help, which we don't want. Users on older scons
        # versions will need to use --variables-help to learn about which variables we support.
        pass

    Return()

if ('CC' in variables_only_env) != ('CXX' in variables_only_env):
    print('Cannot customize C compiler without customizing C++ compiler, and vice versa')
    Exit(1)

# --- environment setup ---

# If the user isn't using the # to indicate top-of-tree or $ to expand a variable, forbid
# relative paths. Relative paths don't really work as expected, because they end up relative to
# the top level SConstruct, not the invokers CWD. We could in theory fix this with
# GetLaunchDir, but that seems a step too far.
buildDir = get_option('build-dir').rstrip('/')
if buildDir[0] not in ['$', '#']:
    if not os.path.isabs(buildDir):
        print("Do not use relative paths with --build-dir")
        Exit(1)

cacheDir = get_option('cache-dir').rstrip('/')
if cacheDir[0] not in ['$', '#']:
    if not os.path.isabs(cacheDir):
        print("Do not use relative paths with --cache-dir")
        Exit(1)

installDir = get_option('prefix').rstrip('/')
if installDir[0] not in ['$', '#']:
    if not os.path.isabs(installDir):
        print("Do not use relative paths with --prefix")
        Exit(1)

sconsDataDir = Dir(buildDir).Dir('scons')
SConsignFile(str(sconsDataDir.File('sconsign')))

def printLocalInfo():
    import sys, SCons
    print( "scons version: " + SCons.__version__ )
    print( "python version: " + " ".join( [ `i` for i in sys.version_info ] ) )

printLocalInfo()

onlyServer = len( COMMAND_LINE_TARGETS ) == 0 or ( len( COMMAND_LINE_TARGETS ) == 1 and str( COMMAND_LINE_TARGETS[0] ) in [ "mongod" , "mongos" , "test" ] )

releaseBuild = has_option("release")

dbg_opt_mapping = {
    # --dbg, --opt   :   dbg    opt
    ( "on",  None  ) : ( True,  False ),  # special case interaction
    ( "on",  "on"  ) : ( True,  True ),
    ( "on",  "off" ) : ( True,  False ),
    ( "off", None  ) : ( False, True ),
    ( "off", "on"  ) : ( False, True ),
    ( "off", "off" ) : ( False, False ),
    ( "on",  "size"  ) : ( True,  True ),
    ( "off", "size"  ) : ( False, True ),
}
debugBuild, optBuild = dbg_opt_mapping[(get_option('dbg'), get_option('opt'))]
optBuildForSize = True if optBuild and get_option('opt') == "size" else False

if releaseBuild and (debugBuild or not optBuild):
    print("Error: A --release build may not have debugging, and must have optimization")
    Exit(1)

noshell = has_option( "noshell" )

jsEngine = get_option( "js-engine")

serverJs = get_option( "server-js" ) == "on"

usemozjs = (jsEngine.startswith('mozjs'))

if not serverJs and not usemozjs:
    print("Warning: --server-js=off is not needed with --js-engine=none")

# We defer building the env until we have determined whether we want certain values. Some values
# in the env actually have semantics for 'None' that differ from being absent, so it is better
# to build it up via a dict, and then construct the Environment in one shot with kwargs.
#
# Yes, BUILD_ROOT vs BUILD_DIR is confusing. Ideally, BUILD_DIR would actually be called
# VARIANT_DIR, and at some point we should probably do that renaming. Until we do though, we
# also need an Environment variable for the argument to --build-dir, which is the parent of all
# variant dirs. For now, we call that BUILD_ROOT. If and when we s/BUILD_DIR/VARIANT_DIR/g,
# then also s/BUILD_ROOT/BUILD_DIR/g.
envDict = dict(BUILD_ROOT=buildDir,
               BUILD_DIR=make_variant_dir_generator(),
               DIST_ARCHIVE_SUFFIX='.tgz',
               DIST_BINARIES=[],
               MODULE_BANNERS=[],
               MODULE_INJECTORS=dict(),
               ARCHIVE_ADDITION_DIR_MAP={},
               ARCHIVE_ADDITIONS=[],
               PYTHON=utils.find_python(),
               SERVER_ARCHIVE='${SERVER_DIST_BASENAME}${DIST_ARCHIVE_SUFFIX}',
               UNITTEST_ALIAS='unittests',
               # TODO: Move unittests.txt to $BUILD_DIR, but that requires
               # changes to MCI.
               UNITTEST_LIST='$BUILD_ROOT/unittests.txt',
               INTEGRATION_TEST_ALIAS='integration_tests',
               INTEGRATION_TEST_LIST='$BUILD_ROOT/integration_tests.txt',
               BENCHMARK_ALIAS='benchmarks',
               BENCHMARK_LIST='$BUILD_ROOT/benchmarks.txt',
               CONFIGUREDIR='$BUILD_ROOT/scons/$VARIANT_DIR/sconf_temp',
               CONFIGURELOG='$BUILD_ROOT/scons/config.log',
               INSTALL_DIR=installDir,
               CONFIG_HEADER_DEFINES={},
               LIBDEPS_TAG_EXPANSIONS=[],
               )

env = Environment(variables=env_vars, **envDict)
del envDict

def fatal_error(env, msg, *args):
    print(msg.format(*args))
    Exit(1)

def conf_error(env, msg, *args):
    print(msg.format(*args))
    print("See {0} for details".format(env.File('$CONFIGURELOG').abspath))
    Exit(1)

env.AddMethod(fatal_error, 'FatalError')
env.AddMethod(conf_error, 'ConfError')

# Normalize the VERBOSE Option, and make its value available as a
# function.
if env['VERBOSE'] == "auto":
    env['VERBOSE'] = not sys.stdout.isatty()
elif env['VERBOSE'] in ('1', "ON", "on", "True", "true", True):
    env['VERBOSE'] = True
elif env['VERBOSE'] in ('0', "OFF", "off", "False", "false", False):
    env['VERBOSE'] = False
else:
    env.FatalError("Invalid value {0} for VERBOSE Variable", env['VERBOSE'])
env.AddMethod(lambda env: env['VERBOSE'], 'Verbose')

if has_option('variables-help'):
    print(env_vars.GenerateHelpText(env))
    Exit(0)

unknown_vars = env_vars.UnknownVariables()
if unknown_vars:
    env.FatalError("Unknown variables specified: {0}", ", ".join(unknown_vars.keys()))

def set_config_header_define(env, varname, varval = 1):
    env['CONFIG_HEADER_DEFINES'][varname] = varval
env.AddMethod(set_config_header_define, 'SetConfigHeaderDefine')

detectEnv = env.Clone()

# Identify the toolchain in use. We currently support the following:
# These macros came from
# http://nadeausoftware.com/articles/2012/10/c_c_tip_how_detect_compiler_name_and_version_using_compiler_predefined_macros
toolchain_macros = {
    'GCC': 'defined(__GNUC__) && !defined(__clang__)',
    'clang': 'defined(__clang__)',
    'MSVC': 'defined(_MSC_VER)'
}

def CheckForToolchain(context, toolchain, lang_name, compiler_var, source_suffix):
    test_body = textwrap.dedent("""
    #if {0}
    /* we are using toolchain {0} */
    #else
    #error
    #endif
    """.format(toolchain_macros[toolchain]))

    print_tuple = (lang_name, context.env[compiler_var], toolchain)
    context.Message('Checking if %s compiler "%s" is %s... ' % print_tuple)

    # Strip indentation from the test body to ensure that the newline at the end of the
    # endif is the last character in the file (rather than a line of spaces with no
    # newline), and that all of the preprocessor directives start at column zero. Both of
    # these issues can trip up older toolchains.
    result = context.TryCompile(test_body, source_suffix)
    context.Result(result)
    return result

endian = get_option( "endian" )

if endian == "auto":
    endian = sys.byteorder

if endian == "little":
    env.SetConfigHeaderDefine("MONGO_CONFIG_BYTE_ORDER", "1234")
elif endian == "big":
    env.SetConfigHeaderDefine("MONGO_CONFIG_BYTE_ORDER", "4321")

# These preprocessor macros came from
# http://nadeausoftware.com/articles/2012/02/c_c_tip_how_detect_processor_type_using_compiler_predefined_macros
#
# NOTE: Remember to add a trailing comma to form any required one
# element tuples, or your configure checks will fail in strange ways.
processor_macros = {
    'arm'     : { 'endian': 'little', 'defines': ('__arm__',) },
    'aarch64' : { 'endian': 'little', 'defines': ('__arm64__', '__aarch64__')},
    'i386'    : { 'endian': 'little', 'defines': ('__i386', '_M_IX86')},
    'ppc64le' : { 'endian': 'little', 'defines': ('__powerpc64__',)},
    's390x'   : { 'endian': 'big',    'defines': ('__s390x__',)},
    'sparc'   : { 'endian': 'big',    'defines': ('__sparc',)},
    'x86_64'  : { 'endian': 'little', 'defines': ('__x86_64', '_M_AMD64')},
}

def CheckForCXXLink(context):
    test_body = """
    #include <iostream>
    #include <cstdlib>

    int main() {
        std::cout << "Hello, World" << std::endl;
        return EXIT_SUCCESS;
    }
    """
    context.Message('Checking that the C++ compiler can link a C++ program... ')
    ret = context.TryLink(textwrap.dedent(test_body), ".cpp")
    context.Result(ret)
    return ret

detectConf = Configure(detectEnv, help=False, custom_tests = {
    'CheckForToolchain' : CheckForToolchain,
    'CheckForCXXLink': CheckForCXXLink,
})

if not detectConf.CheckCC():
    env.ConfError(
        "C compiler {0} doesn't work",
        detectEnv['CC'])

if not detectConf.CheckCXX():
    env.ConfError(
        "C++ compiler {0} doesn't work",
        detectEnv['CXX'])

if not detectConf.CheckForCXXLink():
    env.ConfError(
        "C++ compiler {0} can't link C++ programs",
        detectEnv['CXX'])

if not detectConf.CheckForToolchain("GCC", "C", "CC", ".c"):
    env.ConfError("Could not find GCC toolchain")

# Now that we've detected the toolchain, we add methods to the env
# to get the canonical name of the toolchain and to test whether
# scons is using a particular toolchain.
def get_toolchain_name(self):
    return detected_toolchain.lower()
def is_toolchain(self, *args):
    actual_toolchain = self.ToolchainName()
    for v in args:
        if v.lower() == actual_toolchain:
            return True
    return False

detectConf.Finish()

env['CC_VERSION'] = mongo_toolchain.get_toolchain_ver(env, 'CC')
env['CXX_VERSION'] = mongo_toolchain.get_toolchain_ver(env, 'CXX')

if not env['HOST_ARCH']:
    env['HOST_ARCH'] = env['TARGET_ARCH']

# In some places we have POSIX vs Windows cpp files, and so there's an additional
# env variable to interpolate their names in child sconscripts

env['TARGET_OS_FAMILY'] = 'posix'

# Currently we only use tcmalloc on windows and linux x86_64. Other
# linux targets (power, s390x, arm) do not currently support tcmalloc.
#
# Normalize the allocator option and store it in the Environment. It
# would be nicer to use SetOption here, but you can't reset user
# options for some strange reason in SCons. Instead, we store this
# option as a new variable in the environment.
if get_option('allocator') == "auto":
    env['MONGO_ALLOCATOR'] = "tcmalloc"
else:
    env['MONGO_ALLOCATOR'] = get_option('allocator')

if has_option("cache"):
    if has_option("gcov"):
        env.FatalError("Mixing --cache and --gcov doesn't work correctly yet. See SERVER-11084")
    env.CacheDir(str(env.Dir(cacheDir)))

# Normalize the link model. If it is auto, then for now both developer and release builds
# use the "static" mode. Somday later, we probably want to make the developer build default
# dynamic, but that will require the hygienic builds project.
link_model = get_option('link-model')
if link_model == "auto":
    link_model = "static"

# The 'object' mode for libdeps is enabled by setting _LIBDEPS to $_LIBDEPS_OBJS. The other two
# modes operate in library mode, enabled by setting _LIBDEPS to $_LIBDEPS_LIBS.
env['_LIBDEPS'] = '$_LIBDEPS_OBJS' if link_model == "object" else '$_LIBDEPS_LIBS'

env['BUILDERS']['ProgramObject'] = env['BUILDERS']['StaticObject']
env['BUILDERS']['LibraryObject'] = env['BUILDERS']['StaticObject']

env['SHARPREFIX'] = '$LIBPREFIX'
env['SHARSUFFIX'] = '${SHLIBSUFFIX}${LIBSUFFIX}'
env['BUILDERS']['SharedArchive'] = SCons.Builder.Builder(
    action=env['BUILDERS']['StaticLibrary'].action,
    emitter='$SHAREMITTER',
    prefix='$SHARPREFIX',
    suffix='$SHARSUFFIX',
    src_suffix=env['BUILDERS']['SharedLibrary'].src_suffix,
)

if link_model.startswith("dynamic"):

    def library(env, target, source, *args, **kwargs):
        sharedLibrary = env.SharedLibrary(target, source, *args, **kwargs)
        sharedArchive = env.SharedArchive(target, source=sharedLibrary[0].sources, *args, **kwargs)
        sharedLibrary.extend(sharedArchive)
        return sharedLibrary

    env['BUILDERS']['Library'] = library
    env['BUILDERS']['LibraryObject'] = env['BUILDERS']['SharedObject']

    # TODO: Ideally, the conditions below should be based on a
    # detection of what linker we are using, not the local OS, but I
    # doubt very much that we will see the mach-o linker on anything
    # other than Darwin, or a BFD/sun-esque linker elsewhere.

    # On Darwin, we need to tell the linker that undefined symbols are
    # resolved via dynamic lookup; otherwise we get build failures. On
    # other unixes, we need to suppress as-needed behavior so that
    # initializers are ensured present, even if there is no visible
    # edge to the library in the symbol graph.
    #
    # NOTE: The darwin linker flag is only needed because the library
    # graph is not a DAG. Once the graph is a DAG, we will require all
    # edges to be expressed, and we should drop the flag. When that
    # happens, we should also add -z,defs flag on ELF platforms to
    # ensure that missing symbols due to unnamed dependency edges
    # result in link errors.
    #
    # NOTE: The `illegal_cyclic_or_unresolved_dependencies_whitelisted`
    # tag can be applied to a library to indicate that it does not (or
    # cannot) completely express all of its required link dependencies.
    # This can occur for four reasons:
    #
    # - No unique provider for the symbol: Some symbols do not have a
    #   unique dependency that provides a definition, in which case it
    #   is impossible for the library to express a dependency edge to
    #   resolve the symbol
    #
    # - The library is part of a cycle: If library A depends on B,
    #   which depends on C, which depends on A, then it is impossible
    #   to express all three edges in SCons, since otherwise there is
    #   no way to sequence building the libraries. The cyclic
    #   libraries actually work at runtime, because some parent object
    #   links all of them.
    #
    # - The symbol is provided by an executable into which the library
    #   will be linked. The mongo::inShutdown symbol is a good
    #   example.
    #
    # - The symbol is provided by a third-party library, outside of our
    #   control.
    #
    # All of these are defects in the linking model. In an effort to
    # eliminate these issues, we have begun tagging those libraries
    # that are affected, and requiring that all non-tagged libraries
    # correctly express all dependencies. As we repair each defective
    # library, we can remove the tag. When all the tags are removed
    # the graph will be acyclic. Libraries which are incomplete for the
    # final reason, "libraries outside of our control", may remain for
    # reasons beyond our control. Such libraries ideally should
    # have no dependencies (and thus be leaves in our linking DAG).
    # If that condition is met, then the graph will be acyclic.

    env.AppendUnique(LINKFLAGS=["-Wl,--no-as-needed"])

    # Using zdefs doesn't work at all with the sanitizers
    if not has_option('sanitize'):

        if link_model == "dynamic-strict":
            env.AppendUnique(SHLINKFLAGS=["-Wl,-z,defs"])
        else:
            # On BFD/gold linker environments, which are not strict by
            # default, we need to add a flag when libraries are not
            # tagged incomplete.
            def libdeps_tags_expand_incomplete(source, target, env, for_signature):
                if ('illegal_cyclic_or_unresolved_dependencies_whitelisted'
                    not in target[0].get_env().get("LIBDEPS_TAGS", [])):
                    return ["-Wl,-z,defs"]
                return []
            env['LIBDEPS_TAG_EXPANSIONS'].append(libdeps_tags_expand_incomplete)

if optBuild:
    env.SetConfigHeaderDefine("MONGO_CONFIG_OPTIMIZED_BUILD")

# Enable the fast decider if exlicltly requested or if in 'auto' mode and not in conflict with other
# options.
if get_option('build-fast-and-loose') == 'on' or \
   (get_option('build-fast-and-loose') == 'auto' and \
    not has_option('release') and \
    not has_option('cache')):
    # See http://www.scons.org/wiki/GoFastButton for details
    env.Decider('MD5-timestamp')
    env.SetOption('max_drift', 1)

# If the user has requested the git decider, enable it if it is available. We want to do this after
# we set the basic decider above, so that we 'chain' to that one.
if get_option('git-decider') == 'on':
    git_decider = Tool('git_decider')
    if git_decider.exists(env):
        git_decider(env)

# On non-windows platforms, we may need to differentiate between flags being used to target an
# executable (like -fPIE), vs those being used to target a (shared) library (like -fPIC). To do so,
# we inject a new family of SCons variables PROG*FLAGS, by reaching into the various COMs.
env["CCCOM"] = env["CCCOM"].replace("$CFLAGS", "$CFLAGS $PROGCFLAGS")
env["CXXCOM"] = env["CXXCOM"].replace("$CXXFLAGS", "$CXXFLAGS $PROGCXXFLAGS")
env["CCCOM"] = env["CCCOM"].replace("$CCFLAGS", "$CCFLAGS $PROGCCFLAGS")
env["CXXCOM"] = env["CXXCOM"].replace("$CCFLAGS", "$CCFLAGS $PROGCCFLAGS")
env["LINKCOM"] = env["LINKCOM"].replace("$LINKFLAGS", "$LINKFLAGS $PROGLINKFLAGS")

if not env.Verbose():
    env.Append( CCCOMSTR = "Compiling $TARGET" )
    env.Append( CXXCOMSTR = env["CCCOMSTR"] )
    env.Append( SHCCCOMSTR = "Compiling $TARGET" )
    env.Append( SHCXXCOMSTR = env["SHCCCOMSTR"] )
    env.Append( LINKCOMSTR = "Linking $TARGET" )
    env.Append( SHLINKCOMSTR = env["LINKCOMSTR"] )
    env.Append( ARCOMSTR = "Generating library $TARGET" )

# Link tools other than mslink don't setup TEMPFILE in LINKCOM,
# disabling SCons automatically falling back to a temp file when
# running link commands that are over MAXLINELENGTH. With our object
# file linking mode, we frequently hit even the large linux command
# line length, so we want it everywhere. If we aren't using mslink,
# add TEMPFILE in. For verbose builds when using a tempfile, we need
# some trickery so that we print the command we are running, and not
# just the invocation of the compiler being fed the command file.
if not 'mslink' in env['TOOLS']:
    if env.Verbose():
        env["LINKCOM"] = "${{TEMPFILE('{0}', '')}}".format(env['LINKCOM'])
        env["SHLINKCOM"] = "${{TEMPFILE('{0}', '')}}".format(env['SHLINKCOM'])
        if not 'libtool' in env['TOOLS']:
            env["ARCOM"] = "${{TEMPFILE('{0}', '')}}".format(env['ARCOM'])
    else:
        env["LINKCOM"] = "${{TEMPFILE('{0}', 'LINKCOMSTR')}}".format(env['LINKCOM'])
        env["SHLINKCOM"] = "${{TEMPFILE('{0}', 'SHLINKCOMSTR')}}".format(env['SHLINKCOM'])
        if not 'libtool' in env['TOOLS']:
            env["ARCOM"] = "${{TEMPFILE('{0}', 'ARCOMSTR')}}".format(env['ARCOM'])

if env['_LIBDEPS'] == '$_LIBDEPS_OBJS':
    # The libraries we build in LIBDEPS_OBJS mode are just placeholders for tracking dependencies.
    # This avoids wasting time and disk IO on them.
    def write_uuid_to_file(env, target, source):
        with open(env.File(target[0]).abspath, 'w') as fake_lib:
            fake_lib.write(str(uuid.uuid4()))
            fake_lib.write('\n')

    def noop_action(env, target, source):
        pass

    env['ARCOM'] = write_uuid_to_file
    env['ARCOMSTR'] = 'Generating placeholder library $TARGET'
    env['RANLIBCOM'] = noop_action
    env['RANLIBCOMSTR'] = 'Skipping ranlib for $TARGET'

libdeps.setup_environment(env, emitting_shared=(link_model.startswith("dynamic")))

# Both the abidw tool and the thin archive tool must be loaded after
# libdeps, so that the scanners they inject can see the library
# dependencies added by libdeps.
if link_model.startswith("dynamic"):
    # Add in the abi linking tool if the user requested and it is
    # supported on this platform.
    if env.get('ABIDW'):
        abilink = Tool('abilink')
        if abilink.exists(env):
            abilink(env)

if env['_LIBDEPS'] == '$_LIBDEPS_LIBS':
    # The following platforms probably aren't using the binutils
    # toolchain, or may be using it for the archiver but not the
    # linker, and binutils currently is the olny thing that supports
    # thin archives. Don't even try on those platforms.
    env.Tool('thin_archive')

env['LINK_LIBGROUP_START'] = '-Wl,--start-group'
env['LINK_LIBGROUP_END'] = '-Wl,--end-group'
# NOTE: The leading and trailing spaces here are important. Do not remove them.
env['LINK_WHOLE_ARCHIVE_LIB_START'] = '-Wl,--whole-archive '
env['LINK_WHOLE_ARCHIVE_LIB_END'] = ' -Wl,--no-whole-archive'

# ---- other build setup -----
if debugBuild:
    env.SetConfigHeaderDefine("MONGO_CONFIG_DEBUG_BUILD")
else:
    env.AppendUnique( CPPDEFINES=[ 'NDEBUG' ] )

env.Append( LIBS=["m"] )
env.Append( LIBS=["resolv"] )

# On linux, C code compiled with gcc/clang -std=c11 causes
# __STRICT_ANSI__ to be set, and that drops out all of the feature
# test definitions, resulting in confusing errors when we run C
# language configure checks and expect to be able to find newer
# POSIX things. Explicitly enabling _XOPEN_SOURCE fixes that, and
# should be mostly harmless as on Linux, these macros are
# cumulative. The C++ compiler already sets _XOPEN_SOURCE, and,
# notably, setting it again does not disable any other feature
# test macros, so this is safe to do. Other platforms like macOS
# and BSD have crazy rules, so don't try this there.
#
# Furthermore, as both C++ compilers appears to unconditioanlly
# define _GNU_SOURCE (because libstdc++ requires it), it seems
# prudent to explicitly add that too, so that C language checks
# see a consistent set of definitions.
env.AppendUnique(
    CPPDEFINES=[
        ('_XOPEN_SOURCE', 700),
        '_GNU_SOURCE',
    ],
)

if get_option('runtime-hardening') == "on":
    # If runtime hardening is requested, then build anything
    # destined for an executable with the necessary flags for PIE.
    env.AppendUnique(
        PROGCCFLAGS=['-fPIE'],
        PROGLINKFLAGS=['-pie'],
    )

# -Winvalid-pch Warn if a precompiled header (see Precompiled Headers) is found in the search path but can't be used.
env.Append( CCFLAGS=["-fno-omit-frame-pointer",
                        "-fno-strict-aliasing",
                        "-ggdb",
                        "-pthread",
                        "-Wall",
                        "-Wsign-compare",
                        "-Wno-unknown-pragmas",
                        "-Winvalid-pch"] )
# env.Append( " -Wconversion" ) TODO: this doesn't really work yet
if not has_option("disable-warnings-as-errors"):
    env.Append( CCFLAGS=["-Werror"] )

env.Append( CXXFLAGS=["-Woverloaded-virtual"] )

# SERVER-9761: Ensure early detection of missing symbols in dependent libraries at program
# startup.
env.Append( LINKFLAGS=["-Wl,-z,now"] )
env.Append( LINKFLAGS=["-rdynamic"] )
env.Append( LINKFLAGS=["-fPIC","-pthread"] )

env.Append( LIBS=["pthread"] )

#make scons colorgcc friendly
for key in ('HOME', 'TERM'):
    try:
        env['ENV'][key] = os.environ[key]
    except KeyError:
        pass

# Python uses APPDATA to determine the location of user installed
# site-packages. If we do not pass this variable down to Python
# subprocesses then anything installed with `pip install --user`
# will be inaccessible leading to import errors.

if has_option( "gcov" ):
    env.Append( CCFLAGS=["-fprofile-arcs", "-ftest-coverage"] )
    env.Append( LINKFLAGS=["-fprofile-arcs", "-ftest-coverage"] )

if optBuild and not optBuildForSize:
    env.Append( CCFLAGS=["-O2"] )
elif optBuild and optBuildForSize: 
    env.Append( CCFLAGS=["-Os"] )
else:
    env.Append( CCFLAGS=["-O0"] )

# Promote linker warnings into errors. We can't yet do this on OS X because its linker considers
# noall_load obsolete and warns about it.
if not has_option("disable-warnings-as-errors"):
    env.Append(
        LINKFLAGS=[
            "-Wl,--fatal-warnings",
        ]
    )

mmapv1 = False
if get_option('mmapv1') == 'auto':
    # The mmapv1 storage engine is only supported on x86
    # targets. Unless explicitly requested, disable it on all other
    # platforms.
    mmapv1 = (env['TARGET_ARCH'] in ['i386', 'x86_64'])
elif get_option('mmapv1') == 'on':
    mmapv1 = True

wiredtiger = False
if get_option('wiredtiger') == 'on':
    # Wiredtiger only supports 64-bit architecture, and will fail to compile on 32-bit
    # so disable WiredTiger automatically on 32-bit since wiredtiger is on by default
    if env['TARGET_ARCH'] == 'i386':
        env.FatalError("WiredTiger is not supported on 32-bit platforms\n"
            "Re-run scons with --wiredtiger=off to build on 32-bit platforms")
    else:
        wiredtiger = True
        env.SetConfigHeaderDefine("MONGO_CONFIG_WIREDTIGER_ENABLED")

mobile_se = False
if get_option('mobile-se') == 'on':
    mobile_se = True

if env['TARGET_ARCH'] == 'i386':
    # If we are using GCC or clang to target 32 bit, set the ISA minimum to 'nocona',
    # and the tuning to 'generic'. The choice of 'nocona' is selected because it
    #  -- includes MMX extenions which we need for tcmalloc on 32-bit
    #  -- can target 32 bit
    #  -- is at the time of this writing a widely-deployed 10 year old microarchitecture
    #  -- is available as a target architecture from GCC 4.0+
    # However, we only want to select an ISA, not the nocona specific scheduling, so we
    # select the generic tuning. For installations where hardware and system compiler rev are
    # contemporaries, the generic scheduling should be appropriate for a wide range of
    # deployed hardware.

    env.Append( CCFLAGS=['-march=nocona', '-mtune=generic'] )

# Needed for auth tests since key files are stored in git with mode 644.
for keysuffix in [ "1" , "2" ]:
    keyfile = "jstests/libs/key%s" % keysuffix
    os.chmod( keyfile , stat.S_IWUSR|stat.S_IRUSR )

# discover modules, and load the (python) module for each module's build.py
mongo_modules = moduleconfig.discover_modules('src/mongo/db/modules', get_option('modules'))
env['MONGO_MODULES'] = [m.name for m in mongo_modules]

# --- check system ---
ssl_provider = None
free_monitoring = get_option("enable-free-mon")

def doConfigure(myenv):
    global wiredtiger
    global ssl_provider
    global free_monitoring

    # Check that the compilers work.
    #
    # TODO: Currently, we have some flags already injected. Eventually, this should test the
    # bare compilers, and we should re-check at the very end that TryCompile and TryLink still
    # work with the flags we have selected.
    compiler_minimum_string = "GCC 5.3.0"
    compiler_test_body = textwrap.dedent(
    """
    #if !defined(__GNUC__) || defined(__clang__)
    #error
    #endif

    #if (__GNUC__ < 5) || (__GNUC__ == 5 && __GNUC_MINOR__ < 3) || (__GNUC__ == 5 && __GNUC_MINOR__ == 3 && __GNUC_PATCHLEVEL__ < 0)
    #error %s or newer is required to build MongoDB
    #endif

    int main(int argc, char* argv[]) {
        return 0;
    }
    """ % compiler_minimum_string)

    def CheckForMinimumCompiler(context, language):
        extension_for = {
            "C" : ".c",
            "C++" : ".cpp",
        }
        context.Message("Checking if %s compiler is %s or newer..." %
                        (language, compiler_minimum_string))
        result = context.TryCompile(compiler_test_body, extension_for[language])
        context.Result(result)
        return result;

    conf = Configure(myenv, help=False, custom_tests = {
        'CheckForMinimumCompiler' : CheckForMinimumCompiler,
    })

    c_compiler_validated = conf.CheckForMinimumCompiler('C')
    cxx_compiler_validated = conf.CheckForMinimumCompiler('C++')

    suppress_invalid = has_option("disable-minimum-compiler-version-enforcement")
    if releaseBuild and suppress_invalid:
        env.FatalError("--disable-minimum-compiler-version-enforcement is forbidden with --release")

    if not (c_compiler_validated and cxx_compiler_validated):
        if not suppress_invalid:
            env.ConfError("ERROR: Refusing to build with compiler that does not meet requirements")
        print("WARNING: Ignoring failed compiler version check per explicit user request.")
        print("WARNING: The build may fail, binaries may crash, or may run but corrupt data...")

    conf.Finish()

    def AddFlagIfSupported(env, tool, extension, flag, link, **mutation):
        def CheckFlagTest(context, tool, extension, flag):
            if link:
                if tool == 'C':
                    test_body = """
                    #include <stdlib.h>
                    #include <stdio.h>
                    int main() {
                        printf("Hello, World!");
                        return EXIT_SUCCESS;
                    }"""
                elif tool == 'C++':
                    test_body = """
                    #include <iostream>
                    #include <cstdlib>
                    int main() {
                        std::cout << "Hello, World!" << std::endl;
                        return EXIT_SUCCESS;
                    }"""
                context.Message('Checking if linker supports %s... ' % (flag))
                ret = context.TryLink(textwrap.dedent(test_body), extension)
            else:
                test_body = ""
                context.Message('Checking if %s compiler supports %s... ' % (tool, flag))
                ret = context.TryCompile(textwrap.dedent(test_body), extension)
            context.Result(ret)
            return ret

        test_mutation = copy.deepcopy(mutation)
        # GCC helpfully doesn't issue a diagnostic on unknown flags of the form -Wno-xxx
        # unless other diagnostics are triggered. That makes it tough to check for support
        # for -Wno-xxx. To work around, if we see that we are testing for a flag of the
        # form -Wno-xxx (but not -Wno-error=xxx), we also add -Wxxx to the flags. GCC does
        # warn on unknown -Wxxx style flags, so this lets us probe for availablity of
        # -Wno-xxx.
        for kw in test_mutation.keys():
            test_flags = test_mutation[kw]
            for test_flag in test_flags:
                if test_flag.startswith("-Wno-") and not test_flag.startswith("-Wno-error="):
                    test_flags.append(re.sub("^-Wno-", "-W", test_flag))

        cloned = env.Clone()
        cloned.Append(**test_mutation)

        # For GCC, we don't need anything since bad flags are already errors, but
        # adding -Werror won't hurt. For clang, bad flags are only warnings, so we need -Werror
        # to make them real errors.
        cloned.Append(CCFLAGS=['-Werror'])
        conf = Configure(cloned, help=False, custom_tests = {
                'CheckFlag' : lambda(ctx) : CheckFlagTest(ctx, tool, extension, flag)
        })
        available = conf.CheckFlag()
        conf.Finish()
        if available:
            env.Append(**mutation)
        return available

    def AddToCFLAGSIfSupported(env, flag):
        return AddFlagIfSupported(env, 'C', '.c', flag, False, CFLAGS=[flag])

    def AddToCCFLAGSIfSupported(env, flag):
        return AddFlagIfSupported(env, 'C', '.c', flag, False, CCFLAGS=[flag])

    def AddToCXXFLAGSIfSupported(env, flag):
        return AddFlagIfSupported(env, 'C++', '.cpp', flag, False, CXXFLAGS=[flag])

    def AddToLINKFLAGSIfSupported(env, flag):
        return AddFlagIfSupported(env, 'C', '.c', flag, True, LINKFLAGS=[flag])

    def AddToSHLINKFLAGSIfSupported(env, flag):
        return AddFlagIfSupported(env, 'C', '.c', flag, True, SHLINKFLAGS=[flag])

    # This warning was added in g++-4.8.
    AddToCCFLAGSIfSupported(myenv, '-Wno-unused-local-typedefs')

    # Clang likes to warn about unused functions, which seems a tad aggressive and breaks
    # -Werror, which we want to be able to use.
    AddToCCFLAGSIfSupported(myenv, '-Wno-unused-function')

    # TODO: Note that the following two flags are added to CCFLAGS even though they are
    # really C++ specific. We need to do this because SCons passes CXXFLAGS *before*
    # CCFLAGS, but CCFLAGS contains -Wall, which re-enables the warnings we are trying to
    # suppress. In the future, we should move all warning flags to CCWARNFLAGS and
    # CXXWARNFLAGS and add these to CCOM and CXXCOM as appropriate.
    #
    # Clang likes to warn about unused private fields, but some of our third_party
    # libraries have such things.
    AddToCCFLAGSIfSupported(myenv, '-Wno-unused-private-field')

    # Prevents warning about using deprecated features (such as auto_ptr in c++11)
    # Using -Wno-error=deprecated-declarations does not seem to work on some compilers,
    # including at least g++-4.6.
    AddToCCFLAGSIfSupported(myenv, "-Wno-deprecated-declarations")

    # As of clang-3.4, this warning appears in v8, and gets escalated to an error.
    AddToCCFLAGSIfSupported(myenv, "-Wno-tautological-constant-out-of-range-compare")

    # As of clang in Android NDK 17, these warnings appears in boost and/or ICU, and get escalated to errors
    AddToCCFLAGSIfSupported(myenv, "-Wno-tautological-constant-compare")
    AddToCCFLAGSIfSupported(myenv, "-Wno-tautological-unsigned-zero-compare")
    AddToCCFLAGSIfSupported(myenv, "-Wno-tautological-unsigned-enum-zero-compare")

    # New in clang-3.4, trips up things mostly in third_party, but in a few places in the
    # primary mongo sources as well.
    AddToCCFLAGSIfSupported(myenv, "-Wno-unused-const-variable")

    # Prevents warning about unused but set variables found in boost version 1.49
    # in boost/date_time/format_date_parser.hpp which does not work for compilers
    # GCC >= 4.6. Error explained in https://svn.boost.org/trac/boost/ticket/6136 .
    AddToCCFLAGSIfSupported(myenv, "-Wno-unused-but-set-variable")

    # This has been suppressed in gcc 4.8, due to false positives, but not in clang.  So
    # we explicitly disable it here.
    AddToCCFLAGSIfSupported(myenv, "-Wno-missing-braces")

    # Suppress warnings about not consistently using override everywhere in a class. It seems
    # very pedantic, and we have a fair number of instances.
    AddToCCFLAGSIfSupported(myenv, "-Wno-inconsistent-missing-override")

    # Don't issue warnings about potentially evaluated expressions
    AddToCCFLAGSIfSupported(myenv, "-Wno-potentially-evaluated-expression")

    # Warn about moves of prvalues, which can inhibit copy elision.
    AddToCXXFLAGSIfSupported(myenv, "-Wpessimizing-move")

    # Warn about redundant moves, such as moving a local variable in a return that is different
    # than the return type.
    AddToCXXFLAGSIfSupported(myenv, "-Wredundant-move")

    # Disable warning about variables that may not be initialized
    # Failures are triggered in the case of boost::optional in GCC 4.8.x
    # TODO: re-evaluate when we move to GCC 5.3
    # see: http://stackoverflow.com/questions/21755206/how-to-get-around-gcc-void-b-4-may-be-used-uninitialized-in-this-funct
    AddToCXXFLAGSIfSupported(myenv, "-Wno-maybe-uninitialized")

    # Disable warning about templates that can't be implicitly instantiated. It is an attempt to
    # make a link error into an easier-to-debug compiler failure, but it triggers false
    # positives if explicit instantiation is used in a TU that can see the full definition. This
    # is a problem at least for the S2 headers.
    AddToCXXFLAGSIfSupported(myenv, "-Wno-undefined-var-template")

    # This warning was added in clang-4.0, but it warns about code that is required on some
    # platforms. Since the warning just states that 'explicit instantiation of [a template] that
    # occurs after an explicit specialization has no effect', it is harmless on platforms where
    # it isn't required
    AddToCXXFLAGSIfSupported(myenv, "-Wno-instantiation-after-specialization")

    # This warning was added in clang-5 and flags many of our lambdas. Since it isn't actively
    # harmful to capture unused variables we are suppressing for now with a plan to fix later.
    AddToCCFLAGSIfSupported(myenv, "-Wno-unused-lambda-capture")

    # This warning was added in clang-5 and incorrectly flags our implementation of
    # exceptionToStatus(). See https://bugs.llvm.org/show_bug.cgi?id=34804
    AddToCCFLAGSIfSupported(myenv, "-Wno-exceptions")


    # Check if we can set "-Wnon-virtual-dtor" when "-Werror" is set. The only time we can't set it is on
    # clang 3.4, where a class with virtual function(s) and a non-virtual destructor throws a warning when
    # it shouldn't.
    def CheckNonVirtualDtor(context):

        test_body = """
        class Base {
        public:
            virtual void foo() const = 0;
        protected:
            ~Base() {};
        };

        class Derived : public Base {
        public:
            virtual void foo() const {}
        };
        """

        context.Message('Checking -Wnon-virtual-dtor for false positives... ')
        ret = context.TryCompile(textwrap.dedent(test_body), ".cpp")
        context.Result(ret)
        return ret

    myenvClone = myenv.Clone()
    myenvClone.Append( CCFLAGS=['-Werror'] )
    myenvClone.Append( CXXFLAGS=["-Wnon-virtual-dtor"] )
    conf = Configure(myenvClone, help=False, custom_tests = {
        'CheckNonVirtualDtor' : CheckNonVirtualDtor,
    })
    if conf.CheckNonVirtualDtor():
        myenv.Append( CXXFLAGS=["-Wnon-virtual-dtor"] )
    conf.Finish()

    if get_option('runtime-hardening') == "on":
        # Enable 'strong' stack protection preferentially, but fall back to 'all' if it is not
        # available. Note that we need to add these to the LINKFLAGS as well, since otherwise we
        # might not link libssp when we need to (see SERVER-12456).
        if AddToCCFLAGSIfSupported(myenv, '-fstack-protector-strong'):
            myenv.Append(
                LINKFLAGS=[
                    '-fstack-protector-strong',
                ]
            )
        elif AddToCCFLAGSIfSupported(myenv, '-fstack-protector-all'):
            myenv.Append(
                LINKFLAGS=[
                    '-fstack-protector-all',
                ]
            )

    usingLibStdCxx = False
    if has_option('libc++'):
        myenv.FatalError('libc++ is currently only supported for clang')
        if AddToCXXFLAGSIfSupported(myenv, '-stdlib=libc++'):
            myenv.Append(LINKFLAGS=['-stdlib=libc++'])
        else:
            myenv.ConfError('libc++ requested, but compiler does not support -stdlib=libc++' )
    else:
        def CheckLibStdCxx(context):
            test_body = """
            #include <vector>
            #if !defined(__GLIBCXX__)
            #error
            #endif
            """

            context.Message('Checking if we are using libstdc++... ')
            ret = context.TryCompile(textwrap.dedent(test_body), ".cpp")
            context.Result(ret)
            return ret

        conf = Configure(myenv, help=False, custom_tests = {
            'CheckLibStdCxx' : CheckLibStdCxx,
        })
        usingLibStdCxx = conf.CheckLibStdCxx()
        conf.Finish()

    if get_option('cxx-std') == "14":
        if not AddToCXXFLAGSIfSupported(myenv, '-std=c++14'):
            myenv.ConfError('Compiler does not honor -std=c++14')
    if not AddToCFLAGSIfSupported(myenv, '-std=c11'):
        myenv.ConfError("C++14 mode selected for C++ files, but can't enable C11 for C files")

    # We appear to have C++14, or at least a flag to enable it. Check that the declared C++
    # language level is not less than C++14, and that we can at least compile an 'auto'
    # expression. We don't check the __cplusplus macro when using MSVC because as of our
    # current required MS compiler version (MSVS 2015 Update 2), they don't set it. If
    # MSFT ever decides (in MSVS 2017?) to define __cplusplus >= 201402L, remove the exception
    # here for _MSC_VER
    def CheckCxx14(context):
        test_body = """
        #ifndef _MSC_VER
        #if __cplusplus < 201402L
        #error
        #endif
        #endif
        auto DeducedReturnTypesAreACXX14Feature() {
            return 0;
        }
        """

        context.Message('Checking for C++14... ')
        ret = context.TryCompile(textwrap.dedent(test_body), ".cpp")
        context.Result(ret)
        return ret

    conf = Configure(myenv, help=False, custom_tests = {
        'CheckCxx14' : CheckCxx14,
    })

    if not conf.CheckCxx14():
        myenv.ConfError('C++14 support is required to build MongoDB')

    conf.Finish()

    def CheckMemset_s(context):
        test_body = """
        #define __STDC_WANT_LIB_EXT1__ 1
        #include <cstring>
        int main(int argc, char* argv[]) {
            void* data = nullptr;
            return memset_s(data, 0, 0, 0);
        }
        """

        context.Message('Checking for memset_s... ')
        ret = context.TryLink(textwrap.dedent(test_body), ".cpp")
        context.Result(ret)
        return ret

    conf = Configure(env, custom_tests = {
        'CheckMemset_s' : CheckMemset_s,
    })
    if conf.CheckMemset_s():
        conf.env.SetConfigHeaderDefine("MONGO_CONFIG_HAVE_MEMSET_S")

    if conf.CheckFunc('strnlen'):
        conf.env.SetConfigHeaderDefine("MONGO_CONFIG_HAVE_STRNLEN")

    conf.Finish()

    # If we are using libstdc++, check to see if we are using a
    # libstdc++ that is older than our GCC minimum of 5.3.0. This is
    # primarly to help people using clang on OS X but forgetting to
    # use --libc++ (or set the target OS X version high enough to get
    # it as the default). We would, ideally, check the __GLIBCXX__
    # version, but for various reasons this is not workable. Instead,
    # we switch on the fact that the <experimental/filesystem> header
    # wasn't introduced until libstdc++ 5.3.0. Yes, this is a terrible
    # hack.
    if usingLibStdCxx:
        def CheckModernLibStdCxx(context):
            test_body = """
            #if !__has_include(<experimental/filesystem>)
            #error "libstdc++ from GCC 5.3.0 or newer is required"
            #endif
            """

            context.Message('Checking for libstdc++ 5.3.0 or better... ')
            ret = context.TryCompile(textwrap.dedent(test_body), ".cpp")
            context.Result(ret)
            return ret

        conf = Configure(myenv, help=False, custom_tests = {
            'CheckModernLibStdCxx' : CheckModernLibStdCxx,
        })

        suppress_invalid = has_option("disable-minimum-compiler-version-enforcement")
        if not conf.CheckModernLibStdCxx() and not suppress_invalid:
            myenv.ConfError("When using libstdc++, MongoDB requires libstdc++ from GCC 5.3.0 or newer")

        conf.Finish()

    if has_option("use-glibcxx-debug"):
        # If we are using a modern libstdc++ and this is a debug build and we control all C++
        # dependencies, then turn on the debugging features in libstdc++.
        # TODO: Need a new check here.
        if not debugBuild:
            myenv.FatalError("--use-glibcxx-debug requires --dbg=on")
        if not usingLibStdCxx:
            myenv.FatalError("--use-glibcxx-debug is only compatible with the GNU implementation "
                "of the C++ standard libary")
        myenv.Append(CPPDEFINES=["_GLIBCXX_DEBUG"]);

    # Check if we are on a POSIX system by testing if _POSIX_VERSION is defined.
    def CheckPosixSystem(context):

        test_body = """
        // POSIX requires the existence of unistd.h, so if we can't include unistd.h, we
        // are definitely not a POSIX system.
        #include <unistd.h>
        #if !defined(_POSIX_VERSION)
        #error not a POSIX system
        #endif
        """

        context.Message('Checking if we are on a POSIX system... ')
        ret = context.TryCompile(textwrap.dedent(test_body), ".c")
        context.Result(ret)
        return ret

    conf = Configure(myenv, help=False, custom_tests = {
        'CheckPosixSystem' : CheckPosixSystem,
    })
    posix_system = conf.CheckPosixSystem()

    conf.Finish()

    # Check if we are on a system that support the POSIX clock_gettime function
    #  and the "monotonic" clock.
    posix_monotonic_clock = False
    if posix_system:
        def CheckPosixMonotonicClock(context):

            test_body = """
            #include <unistd.h>
            #if !(defined(_POSIX_TIMERS) && _POSIX_TIMERS > 0)
            #error POSIX clock_gettime not supported
            #elif !(defined(_POSIX_MONOTONIC_CLOCK) && _POSIX_MONOTONIC_CLOCK >= 0)
            #error POSIX monotonic clock not supported
            #endif
            """

            context.Message('Checking if the POSIX monotonic clock is supported... ')
            ret = context.TryCompile(textwrap.dedent(test_body), ".c")
            context.Result(ret)
            return ret

        conf = Configure(myenv, help=False, custom_tests = {
            'CheckPosixMonotonicClock' : CheckPosixMonotonicClock,
        })
        posix_monotonic_clock = conf.CheckPosixMonotonicClock()

        # On 32-bit systems, we need to define this in order to get access to
        # the 64-bit versions of fseek, etc.
        if not conf.CheckTypeSize('off_t', includes="#include <sys/types.h>", expect=8):
            myenv.Append(CPPDEFINES=["_FILE_OFFSET_BITS=64"])

        conf.Finish()

    if has_option('sanitize'):

        # GCC's implementation of ASAN depends on libdl.
        env.Append(LIBS=['dl'])

        if env['MONGO_ALLOCATOR'] == 'tcmalloc':
            # There are multiply defined symbols between the sanitizer and
            # our vendorized tcmalloc.
            env.FatalError("Cannot use --sanitize with tcmalloc")

        sanitizer_list = get_option('sanitize').split(',')

        using_lsan = 'leak' in sanitizer_list
        using_asan = 'address' in sanitizer_list or using_lsan
        using_tsan = 'thread' in sanitizer_list
        using_ubsan = 'undefined' in sanitizer_list

        # If the user asked for leak sanitizer, turn on the detect_leaks
        # ASAN_OPTION. If they asked for address sanitizer as well, drop
        # 'leak', because -fsanitize=leak means no address.
        #
        # --sanitize=leak:           -fsanitize=leak, detect_leaks=1
        # --sanitize=address,leak:   -fsanitize=address, detect_leaks=1
        # --sanitize=address:        -fsanitize=address
        #
        if using_lsan:
            if using_asan:
                myenv['ENV']['ASAN_OPTIONS'] = "detect_leaks=1"
            myenv['ENV']['LSAN_OPTIONS'] = "suppressions=%s" % myenv.File("#etc/lsan.suppressions").abspath
            if 'address' in sanitizer_list:
                sanitizer_list.remove('leak')

        sanitizer_option = '-fsanitize=' + ','.join(sanitizer_list)

        if AddToCCFLAGSIfSupported(myenv, sanitizer_option):
            myenv.Append(LINKFLAGS=[sanitizer_option])
            myenv.Append(CCFLAGS=['-fno-omit-frame-pointer'])
        else:
            myenv.ConfError('Failed to enable sanitizers with flag: {0}', sanitizer_option )

        blackfiles_map = {
            "address" : myenv.File("#etc/asan.blacklist"),
            "leak" : myenv.File("#etc/asan.blacklist"),
            "thread" : myenv.File("#etc/tsan.blacklist"),
            "undefined" : myenv.File("#etc/ubsan.blacklist"),
        }

        # Select those unique black files that are associated with the
        # currently enabled sanitizers, but filter out those that are
        # zero length.
        blackfiles = {v for (k, v) in blackfiles_map.iteritems() if k in sanitizer_list}
        blackfiles = [f for f in blackfiles if os.stat(f.path).st_size != 0]

        # Filter out any blacklist options that the toolchain doesn't support.
        supportedBlackfiles = []
        blackfilesTestEnv = myenv.Clone()
        for blackfile in blackfiles:
            if AddToCCFLAGSIfSupported(blackfilesTestEnv, "-fsanitize-blacklist=%s" % blackfile):
                supportedBlackfiles.append(blackfile)
        blackfilesTestEnv = None
        blackfiles = sorted(supportedBlackfiles)

        # If we ended up with any blackfiles after the above filters,
        # then expand them into compiler flag arguments, and use a
        # generator to return at command line expansion time so that
        # we can change the signature if the file contents change.
        if blackfiles:
            blacklist_options=["-fsanitize-blacklist=%s" % blackfile for blackfile in blackfiles]
            def SanitizerBlacklistGenerator(source, target, env, for_signature):
                if for_signature:
                    return [f.get_csig() for f in blackfiles]
                return blacklist_options
            myenv.AppendUnique(
                SANITIZER_BLACKLIST_GENERATOR=SanitizerBlacklistGenerator,
                CCFLAGS="${SANITIZER_BLACKLIST_GENERATOR}",
                LINKFLAGS="${SANITIZER_BLACKLIST_GENERATOR}",
            )

        llvm_symbolizer = get_option('llvm-symbolizer')
        if os.path.isabs(llvm_symbolizer):
            if not myenv.File(llvm_symbolizer).exists():
                print("WARNING: Specified symbolizer '%s' not found" % llvm_symbolizer)
                llvm_symbolizer = None
        else:
            llvm_symbolizer = myenv.WhereIs(llvm_symbolizer)

        tsan_options = ""
        if llvm_symbolizer:
            myenv['ENV']['ASAN_SYMBOLIZER_PATH'] = llvm_symbolizer
            myenv['ENV']['LSAN_SYMBOLIZER_PATH'] = llvm_symbolizer
            tsan_options = "external_symbolizer_path=\"%s\" " % llvm_symbolizer
        elif using_lsan:
            myenv.FatalError("Using the leak sanitizer requires a valid symbolizer")

        if using_tsan:
            tsan_options += "suppressions=\"%s\" " % myenv.File("#etc/tsan.suppressions").abspath
            myenv['ENV']['TSAN_OPTIONS'] = tsan_options

        if using_ubsan:
            # By default, undefined behavior sanitizer doesn't stop on
            # the first error. Make it so. Newer versions of clang
            # have renamed the flag.
            if not AddToCCFLAGSIfSupported(myenv, "-fno-sanitize-recover"):
                AddToCCFLAGSIfSupported(myenv, "-fno-sanitize-recover=undefined")

    # This tells clang/gcc to use the gold linker if it is available - we prefer the gold linker
    # because it is much faster. Don't use it if the user has already configured another linker
    # selection manually.
    if not any(flag.startswith('-fuse-ld=') for flag in env['LINKFLAGS']):
        AddToLINKFLAGSIfSupported(myenv, '-fuse-ld=gold')

    # Explicitly enable GNU build id's if the linker supports it.
    AddToLINKFLAGSIfSupported(myenv, '-Wl,--build-id')

    # Explicitly use the new gnu hash section if the linker offers
    # support it. For that platform, use 'both'.
    AddToLINKFLAGSIfSupported(myenv, '-Wl,--hash-style=gnu')

    # Try to have the linker tell us about ODR violations. Don't
    # use it when using clang with libstdc++, as libstdc++ was
    # probably built with GCC. That combination appears to cause
    # false positives for the ODR detector. See SERVER-28133 for
    # additional details.
    if (get_option('detect-odr-violations')):
        AddToLINKFLAGSIfSupported(myenv, '-Wl,--detect-odr-violations')

    # Disallow an executable stack. Also, issue a warning if any files are found that would
    # cause the stack to become executable if the noexecstack flag was not in play, so that we
    # can find them and fix them. We do this here after we check for ld.gold because the
    # --warn-execstack is currently only offered with gold.
    #
    # TODO: Add -Wl,--fatal-warnings once WT-2629 is fixed. We probably can do that
    # unconditionally above, and not need to do it as an AddToLINKFLAGSIfSupported step, since
    # both gold and binutils ld both support it.
    AddToLINKFLAGSIfSupported(myenv, "-Wl,-z,noexecstack")
    AddToLINKFLAGSIfSupported(myenv, "-Wl,--warn-execstack")

    # If possible with the current linker, mark relocations as read-only.
    AddToLINKFLAGSIfSupported(myenv, "-Wl,-z,relro")

    # Apply any link time optimization settings as selected by the 'lto' option.
    if has_option('lto'):
        # For GCC and clang, the flag is -flto, and we need to pass it both on the compile
        # and link lines.
        if not AddToCCFLAGSIfSupported(myenv, '-flto') or \
                not AddToLINKFLAGSIfSupported(myenv, '-flto'):
            myenv.ConfError("Link time optimization requested, "
                "but selected compiler does not honor -flto" )

    if get_option('runtime-hardening') == "on" and optBuild:
        # Older glibc doesn't work well with _FORTIFY_SOURCE=2. Selecting 2.11 as the minimum was an
        # emperical decision, as that is the oldest non-broken glibc we seem to require. It is possible
        # that older glibc's work, but we aren't trying.
        #
        # https://gforge.inria.fr/tracker/?func=detail&group_id=131&atid=607&aid=14070
        # https://github.com/jedisct1/libsodium/issues/202
        def CheckForGlibcKnownToSupportFortify(context):
            test_body="""
            #include <features.h>
            #if !__GLIBC_PREREQ(2, 11)
            #error
            #endif
            """
            context.Message('Checking for glibc with non-broken _FORTIFY_SOURCE...')
            ret = context.TryCompile(textwrap.dedent(test_body), ".c")
            context.Result(ret)
            return ret

        conf = Configure(myenv, help=False, custom_tests = {
            'CheckForFortify': CheckForGlibcKnownToSupportFortify,
        })

        # Fortify only possibly makes sense on POSIX systems, and we know that clang is not a valid
        # combination:
        #
        # http://lists.llvm.org/pipermail/cfe-dev/2015-November/045852.html
        #
        if conf.CheckForFortify():
            conf.env.Append(
                CPPDEFINES=[
                    ('_FORTIFY_SOURCE', 2),
                ],
            )

        myenv = conf.Finish()

    # We set this to work around https://gcc.gnu.org/bugzilla/show_bug.cgi?id=43052
    AddToCCFLAGSIfSupported(myenv, "-fno-builtin-memcmp")

    def CheckThreadLocal(context):
        test_body = """
        thread_local int tsp_int = 1;
        int main(int argc, char** argv) {{
            return !(tsp_int == argc);
        }}
        """
        context.Message('Checking for storage class thread_local ')
        ret = context.TryLink(textwrap.dedent(test_body), ".cpp")
        context.Result(ret)
        return ret

    conf = Configure(myenv, help=False, custom_tests = {
        'CheckThreadLocal': CheckThreadLocal
    })
    if not conf.CheckThreadLocal():
        env.ConfError("Compiler must support the thread_local storage class")
    conf.Finish()

    def CheckCXX14EnableIfT(context):
        test_body = """
        #include <cstdlib>
        #include <type_traits>

        template <typename = void>
        struct scons {
            bool hasSupport() { return false; }
        };

        template <>
        struct scons<typename std::enable_if_t<true>> {
            bool hasSupport() { return true; }
        };

        int main(int argc, char **argv) {
            scons<> SCons;
            return SCons.hasSupport() ? EXIT_SUCCESS : EXIT_FAILURE;
        }
        """
        context.Message('Checking for C++14 std::enable_if_t support...')
        ret = context.TryCompile(textwrap.dedent(test_body), '.cpp')
        context.Result(ret)
        return ret

    # Check for std::enable_if_t support without using the __cplusplus macro
    conf = Configure(myenv, help=False, custom_tests = {
        'CheckCXX14EnableIfT' : CheckCXX14EnableIfT,
    })

    if conf.CheckCXX14EnableIfT():
        conf.env.SetConfigHeaderDefine('MONGO_CONFIG_HAVE_STD_ENABLE_IF_T')

    myenv = conf.Finish()

    def CheckCXX14MakeUnique(context):
        test_body = """
        #include <memory>
        int main(int argc, char **argv) {
            auto foo = std::make_unique<int>(5);
            return 0;
        }
        """
        context.Message('Checking for C++14 std::make_unique support... ')
        ret = context.TryCompile(textwrap.dedent(test_body), '.cpp')
        context.Result(ret)
        return ret

    # Check for std::make_unique support without using the __cplusplus macro
    conf = Configure(myenv, help=False, custom_tests = {
        'CheckCXX14MakeUnique': CheckCXX14MakeUnique,
    })

    if conf.CheckCXX14MakeUnique():
        conf.env.SetConfigHeaderDefine('MONGO_CONFIG_HAVE_STD_MAKE_UNIQUE')

    # pthread_setname_np was added in GLIBC 2.12, and Solaris 11.3
    if posix_system:
        myenv = conf.Finish()

        def CheckPThreadSetNameNP(context):
            compile_test_body = textwrap.dedent("""
            #ifndef _GNU_SOURCE
            #define _GNU_SOURCE
            #endif
            #include <pthread.h>

            int main() {
                pthread_setname_np(pthread_self(), "test");
                return 0;
            }
            """)

            context.Message("Checking if pthread_setname_np is supported... ")
            result = context.TryCompile(compile_test_body, ".cpp")
            context.Result(result)
            return result

        conf = Configure(myenv, custom_tests = {
            'CheckPThreadSetNameNP': CheckPThreadSetNameNP,
        })

        if conf.CheckPThreadSetNameNP():
            conf.env.SetConfigHeaderDefine("MONGO_CONFIG_HAVE_PTHREAD_SETNAME_NP")

    myenv = conf.Finish()

    def CheckBoostMinVersion(context):
        compile_test_body = textwrap.dedent("""
        #include <boost/version.hpp>

        #if BOOST_VERSION < 104900
        #error
        #endif
        """)

        context.Message("Checking if system boost version is 1.49 or newer...")
        result = context.TryCompile(compile_test_body, ".cpp")
        context.Result(result)
        return result

    conf = Configure(myenv, custom_tests = {
        'CheckBoostMinVersion': CheckBoostMinVersion,
    })

    libdeps.setup_conftests(conf)

    ### --ssl and --ssl-provider checks
    def checkOpenSSL(conf):
        sslLibName = "ssl"
        cryptoLibName = "crypto"
        sslLinkDependencies = ["crypto", "dl"]

        if not conf.CheckLibWithHeader(
                cryptoLibName,
                ["openssl/crypto.h"],
                "C",
                "SSLeay_version(0);",
                autoadd=True):
            maybeIssueDarwinSSLAdvice(conf.env)
            conf.env.ConfError("Couldn't find OpenSSL crypto.h header and library")

        def CheckLibSSL(context):
            res = SCons.Conftest.CheckLib(context,
                     libs=[sslLibName],
                     extra_libs=sslLinkDependencies,
                     header='#include "openssl/ssl.h"',
                     language="C",
                     call="SSL_version(NULL);",
                     autoadd=True)
            context.did_show_result = 1
            return not res

        conf.AddTest("CheckLibSSL", CheckLibSSL)

        if not conf.CheckLibSSL():
           maybeIssueDarwinSSLAdvice(conf.env)
           conf.env.ConfError("Couldn't find OpenSSL ssl.h header and library")

        def CheckLinkSSL(context):
            test_body = """
            #include <openssl/err.h>
            #include <openssl/ssl.h>
            #include <stdlib.h>

            int main() {
                SSL_library_init();
                SSL_load_error_strings();
                ERR_load_crypto_strings();

                OpenSSL_add_all_algorithms();
                ERR_free_strings();

                return EXIT_SUCCESS;
            }
            """
            context.Message("Checking that linking to OpenSSL works...")
            ret = context.TryLink(textwrap.dedent(test_body), ".c")
            context.Result(ret)
            return ret

        conf.AddTest("CheckLinkSSL", CheckLinkSSL)

        if not conf.CheckLinkSSL():
            maybeIssueDarwinSSLAdvice(conf.env)
            conf.env.ConfError("SSL is enabled, but is unavailable")

        if conf.CheckDeclaration(
            "FIPS_mode_set",
            includes="""
                #include <openssl/crypto.h>
                #include <openssl/evp.h>
            """):
            conf.env.SetConfigHeaderDefine('MONGO_CONFIG_HAVE_FIPS_MODE_SET')

        if conf.CheckDeclaration(
            "d2i_ASN1_SEQUENCE_ANY",
            includes="""
                #include <openssl/asn1.h>
            """):
            conf.env.SetConfigHeaderDefine('MONGO_CONFIG_HAVE_ASN1_ANY_DEFINITIONS')

        def CheckOpenSSL_EC_DH(context):
            compile_test_body = textwrap.dedent("""
            #include <openssl/ssl.h>

            int main() {
                SSL_CTX_set_ecdh_auto(0, 0);
                SSL_set_ecdh_auto(0, 0);
                return 0;
            }
            """)

            context.Message("Checking if SSL_[CTX_]_set_ecdh_auto is supported... ")
            result = context.TryCompile(compile_test_body, ".cpp")
            context.Result(result)
            return result

        conf.AddTest("CheckOpenSSL_EC_DH", CheckOpenSSL_EC_DH)
        if conf.CheckOpenSSL_EC_DH():
            conf.env.SetConfigHeaderDefine('MONGO_CONFIG_HAVE_SSL_SET_ECDH_AUTO')

    ssl_provider = get_option("ssl-provider")
    if ssl_provider == 'auto':
        ssl_provider = 'openssl'

    if ssl_provider == 'openssl':
        if has_option("ssl"):
            checkOpenSSL(conf)
            # Working OpenSSL available, use it.
            env.SetConfigHeaderDefine("MONGO_CONFIG_SSL_PROVIDER", "MONGO_CONFIG_SSL_PROVIDER_OPENSSL")

            conf.env.Append( MONGO_CRYPTO=["openssl"] )
        else:
            # If we don't need an SSL build, we can get by with TomCrypt.
            conf.env.Append( MONGO_CRYPTO=["tom"] )

    if has_option( "ssl" ):
        # Either crypto engine is native,
        # or it's OpenSSL and has been checked to be working.
        conf.env.SetConfigHeaderDefine("MONGO_CONFIG_SSL")
        print("Using SSL Provider: {0}".format(ssl_provider))
    else:
        ssl_provider = "none"

    if free_monitoring == "auto":
        if "enterprise" not in env['MONGO_MODULES']:
            free_monitoring = "on"
        else:
            free_monitoring = "off"

    conf.FindSysLibDep("stemmer", ["stemmer"])

    conf.FindSysLibDep("snappy", ["snappy"])

    conf.FindSysLibDep("benchmark", ["benchmark"])

    conf.CheckLib('pcre')
    conf.CheckLib('pcrecpp')

    conf.FindSysLibDep("pcre", ["pcre"])
    conf.FindSysLibDep("pcrecpp", ["pcrecpp"])

    conf.FindSysLibDep("zlib", ["z"])

    conf.FindSysLibDep("yaml", ["yaml-cpp"])

    if not conf.CheckCXXHeader( "sqlite3.h" ):
        myenv.ConfError("Cannot find sqlite headers")
    conf.FindSysLibDep("sqlite", ["sqlite3"])

    conf.env.Append(
        CPPDEFINES=[
            ('UCONFIG_NO_BREAK_ITERATION', 1),
            ('UCONFIG_NO_FORMATTING', 1),
            ('UCONFIG_NO_TRANSLITERATION', 1),
            ('UCONFIG_NO_REGULAR_EXPRESSIONS', 1),
            ('U_CHARSET_IS_UTF8', 1),
            ('U_DISABLE_RENAMING', 0),
            ('U_STATIC_IMPLEMENTATION', 1),
            ('U_USING_ICU_NAMESPACE', 0),
        ],
    )

    #env.Append(LIBS=['icudata','icui18n','icuuc'])
    conf.FindSysLibDep("icudata", ["icudata"])
    #conf.FindSysLibDep("icui18n", ["icui18n"])
    #conf.FindSysLibDep("icuuc", ["icuuc"])
    # We can't use FindSysLibDep() for icui18n and icuuc below, since SConf.CheckLib() (which
    # FindSysLibDep() relies on) doesn't expose an 'extra_libs' parameter to indicate that the
    # library being tested has additional dependencies (icuuc depends on icudata, and icui18n
    # depends on both). As a workaround, we skip the configure check for these two libraries and
    # manually assign the library name. We hope that if the user has icudata installed on their
    # system, then they also have icu18n and icuuc installed.
    conf.env['LIBDEPS_ICUI18N_SYSLIBDEP'] = 'icui18n'
    conf.env['LIBDEPS_ICUUC_SYSLIBDEP'] = 'icuuc'

    conf.env.Append(
        CPPDEFINES=[
            "BOOST_SYSTEM_NO_DEPRECATED",
            "BOOST_MATH_NO_LONG_DOUBLE_MATH_FUNCTIONS",
        ]
    )

    if not conf.CheckCXXHeader( "boost/filesystem/operations.hpp" ):
        myenv.ConfError("can't find boost headers")
    if not conf.CheckBoostMinVersion():
        myenv.ConfError("system's version of boost is too old. version 1.49 or better required")

    conf.FindSysLibDep("boost_filesystem",["boost_filesystem"],language='C++');
    conf.FindSysLibDep("boost_program_options",["boost_program_options"],language='C++');
    conf.FindSysLibDep("boost_system",["boost_system"],language='C++');
    
    env.Append(LIBS=['z','lzma','zstd'])
    conf.FindSysLibDep("boost_iostreams",["boost_iostreams"],language='C++');
    env.Append(LIBS=[])
    
    if posix_system:
        conf.env.SetConfigHeaderDefine("MONGO_CONFIG_HAVE_HEADER_UNISTD_H")
        conf.CheckLib('rt')
        conf.CheckLib('dl')

    if posix_monotonic_clock:
        conf.env.SetConfigHeaderDefine("MONGO_CONFIG_HAVE_POSIX_MONOTONIC_CLOCK")

    if (conf.CheckCXXHeader( "execinfo.h" ) and
        conf.CheckDeclaration('backtrace', includes='#include <execinfo.h>') and
        conf.CheckDeclaration('backtrace_symbols', includes='#include <execinfo.h>') and
        conf.CheckDeclaration('backtrace_symbols_fd', includes='#include <execinfo.h>')):

        conf.env.SetConfigHeaderDefine("MONGO_CONFIG_HAVE_EXECINFO_BACKTRACE")

    conf.env["_HAVEPCAP"] = conf.CheckLib( ["pcap", "wpcap"], autoadd=False )


    conf.env['MONGO_BUILD_SASL_CLIENT'] = bool(has_option("use-sasl-client"))
    if conf.env['MONGO_BUILD_SASL_CLIENT'] and not conf.CheckLibWithHeader(
            "sasl2",
            ["stddef.h","sasl/sasl.h"],
            "C",
            "sasl_version_info(0, 0, 0, 0, 0, 0);",
            autoadd=False ):
        myenv.ConfError("Couldn't find SASL header/libraries")

    # 'tcmalloc' needs to be the last library linked. Please, add new libraries before this
    # point.
    if myenv['MONGO_ALLOCATOR'] == 'tcmalloc':
        conf.FindSysLibDep("tcmalloc", ["tcmalloc_minimal"])
    elif myenv['MONGO_ALLOCATOR'] in ['system', 'tcmalloc-experimental']:
        pass
    else:
        myenv.FatalError("Invalid --allocator parameter: $MONGO_ALLOCATOR")

    def CheckStdAtomic(context, base_type, extra_message):
        test_body = """
        #include <atomic>

        int main() {{
            std::atomic<{0}> x;

            x.store(0);
            {0} y = 1;
            x.fetch_add(y);
            x.fetch_sub(y);
            x.exchange(y);
            x.compare_exchange_strong(y, x);
            x.is_lock_free();
            return x.load();
        }}
        """.format(base_type)

        context.Message(
            "Checking if std::atomic<{0}> works{1}... ".format(
                base_type, extra_message
            )
        )

        ret = context.TryLink(textwrap.dedent(test_body), ".cpp")
        context.Result(ret)
        return ret
    conf.AddTest("CheckStdAtomic", CheckStdAtomic)

    def check_all_atomics(extra_message=''):
        for t in ('int64_t', 'uint64_t', 'int32_t', 'uint32_t'):
            if not conf.CheckStdAtomic(t, extra_message):
                return False
        return True

    if not check_all_atomics():
        if not conf.CheckLib('atomic', symbol=None, header=None, language='C', autoadd=1):
            myenv.ConfError("Some atomic ops are not intrinsically supported, but "
                "no libatomic found")
        if not check_all_atomics(' with libatomic'):
            myenv.ConfError("The toolchain does not support std::atomic, cannot continue")

    def CheckExtendedAlignment(context, size):
        test_body = """
            #include <atomic>
            #include <mutex>
            #include <cstddef>

            static_assert(alignof(std::max_align_t) < {0}, "whatever");

            alignas({0}) std::mutex aligned_mutex;
            alignas({0}) std::atomic<int> aligned_atomic;

            struct alignas({0}) aligned_struct_mutex {{
                std::mutex m;
            }};

            struct alignas({0}) aligned_struct_atomic {{
                std::atomic<int> m;
            }};

            struct holds_aligned_mutexes {{
                alignas({0}) std::mutex m1;
                alignas({0}) std::mutex m2;
            }} hm;

            struct holds_aligned_atomics {{
                alignas({0}) std::atomic<int> a1;
                alignas({0}) std::atomic<int> a2;
            }} ha;
        """.format(size)

        context.Message('Checking for extended alignment {0} for concurrency types... '.format(size))
        ret = context.TryCompile(textwrap.dedent(test_body), ".cpp")
        context.Result(ret)
        return ret

    conf.AddTest('CheckExtendedAlignment', CheckExtendedAlignment)

    # If we don't have a specialized search sequence for this
    # architecture, assume 64 byte cache lines, which is pretty
    # standard. If for some reason the compiler can't offer that, try
    # 32.
    default_alignment_search_sequence = [ 64, 32 ]

    # The following are the target architectures for which we have
    # some knowledge that they have larger cache line sizes. In
    # particular, POWER8 uses 128 byte lines and zSeries uses 256. We
    # start at the goal state, and work down until we find something
    # the compiler can actualy do for us.
    extended_alignment_search_sequence = {
        'ppc64le' : [ 128, 64, 32 ],
        's390x' : [ 256, 128, 64, 32 ],
    }

    for size in extended_alignment_search_sequence.get(env['TARGET_ARCH'], default_alignment_search_sequence):
        if conf.CheckExtendedAlignment(size):
            conf.env.SetConfigHeaderDefine("MONGO_CONFIG_MAX_EXTENDED_ALIGNMENT", size)
            break
 
    def CheckMongoCMinVersion(context):
        compile_test_body = textwrap.dedent("""
        #include <mongoc/mongoc.h>

        #if !MONGOC_CHECK_VERSION(1,13,0)
        #error
        #endif
        """)

        context.Message("Checking if mongoc version is 1.13.0 or newer...")
        result = context.TryCompile(compile_test_body, ".cpp")
        context.Result(result)
        return result

    conf.AddTest('CheckMongoCMinVersion', CheckMongoCMinVersion)
    
    mongoc_mode = get_option('use-system-mongo-c')
    conf.env['MONGO_HAVE_LIBMONGOC'] = False
    if mongoc_mode != 'off':
        if conf.CheckLibWithHeader(
                ["mongoc-1.0"],
                ["mongoc/mongoc.h"],
                "C",
                "mongoc_get_major_version();",
                autoadd=False ):
            conf.env['MONGO_HAVE_LIBMONGOC'] = "library" 
        if not conf.env['MONGO_HAVE_LIBMONGOC'] and mongoc_mode == 'on':
            myenv.ConfError("Failed to find the required C driver headers")
        if conf.env['MONGO_HAVE_LIBMONGOC'] and not conf.CheckMongoCMinVersion():
            myenv.ConfError("Version of mongoc is too old. Version 1.13+ required")

    # ask each module to configure itself and the build environment.
    moduleconfig.configure_modules(mongo_modules, conf)

    if env['TARGET_ARCH'] == "ppc64le":
        # This checks for an altivec optimization we use in full text search.
        # Different versions of gcc appear to put output bytes in different
        # parts of the output vector produced by vec_vbpermq.  This configure
        # check looks to see which format the compiler produces.
        #
        # NOTE: This breaks cross compiles, as it relies on checking runtime functionality for the
        # environment we're in.  A flag to choose the index, or the possibility that we don't have
        # multiple versions to support (after a compiler upgrade) could solve the problem if we
        # eventually need them.
        def CheckAltivecVbpermqOutput(context, index):
            test_body = """
                #include <altivec.h>
                #include <cstring>
                #include <cstdint>
                #include <cstdlib>

                int main() {{
                    using Native = __vector signed char;
                    const size_t size = sizeof(Native);
                    const Native bits = {{ 120, 112, 104, 96, 88, 80, 72, 64, 56, 48, 40, 32, 24, 16, 8, 0 }};

                    uint8_t inputBuf[size];
                    std::memset(inputBuf, 0xFF, sizeof(inputBuf));

                    for (size_t offset = 0; offset <= size; offset++) {{
                        Native vec = vec_vsx_ld(0, reinterpret_cast<const Native*>(inputBuf));

                        uint64_t mask = vec_extract(vec_vbpermq(vec, bits), {0});

                        size_t initialZeros = (mask == 0 ? size : __builtin_ctzll(mask));
                        if (initialZeros != offset) {{
			    return 1;
                        }}

                        if (offset < size) {{
                            inputBuf[offset] = 0;  // Add an initial 0 for the next loop.
                        }}
                    }}

		    return 0;
                }}
            """.format(index)

            context.Message('Checking for vec_vbperm output in index {0}... '.format(index))
            ret = context.TryRun(textwrap.dedent(test_body), ".cpp")
            context.Result(ret[0])
            return ret[0]

        conf.AddTest('CheckAltivecVbpermqOutput', CheckAltivecVbpermqOutput)

        outputIndex = next((idx for idx in [0,1] if conf.CheckAltivecVbpermqOutput(idx)), None)
        if outputIndex is not None:
	    conf.env.SetConfigHeaderDefine("MONGO_CONFIG_ALTIVEC_VEC_VBPERMQ_OUTPUT_INDEX", outputIndex)
        else:
            myenv.ConfError("Running on ppc64le, but can't find a correct vec_vbpermq output index.  Compiler or platform not supported")

    return conf.Finish()

env = doConfigure( env )

# TODO: Later, this should live somewhere more graceful.
if get_option('install-mode') == 'hygienic':

    if get_option('separate-debug') == "on":
        env.Tool('separate_debug')

    env.Tool('auto_install_binaries')
    env.AppendUnique(
        RPATH=[
            env.Literal('\\$$ORIGIN/../lib')
        ],
        LINKFLAGS=[
            '-Wl,-z,origin',
            '-Wl,--enable-new-dtags',
        ],
        SHLINKFLAGS=[
            # -h works for both the sun linker and the gnu linker.
            "-Wl,-h,${TARGET.file}",
        ]
    )

elif get_option('separate-debug') == "on":
    env.FatalError('Cannot use --separate-debug without --install-mode=hygienic')

# Now that we are done with configure checks, enable icecream, if available.
env.Tool('icecream')

# If the flags in the environment are configured for -gsplit-dwarf,
# inject the necessary emitter.
split_dwarf = Tool('split_dwarf')
if split_dwarf.exists(env):
    split_dwarf(env)

# Load the compilation_db tool. We want to do this after configure so we don't end up with
# compilation database entries for the configure tests, which is weird.
env.Tool("compilation_db")

# If we can, load the dagger tool for build dependency graph introspection.
# Dagger is only supported on Linux and OSX (not Windows or Solaris).
should_dagger = ( mongo_platform.is_running_os('osx') or mongo_platform.is_running_os('linux')  ) and "dagger" in COMMAND_LINE_TARGETS

if should_dagger:
    env.Tool("dagger")

incremental_link = Tool('incremental_link')
if incremental_link.exists(env):
    incremental_link(env)

def checkErrorCodes():
    import buildscripts.errorcodes as x
    if x.check_error_codes() == False:
        env.FatalError("next id to use: {0}", x.get_next_code())

checkErrorCodes()

# --- lint ----

def doLint( env , target , source ):
    import buildscripts.eslint
    if not buildscripts.eslint.lint(None, dirmode=True, glob=["jstests/", "src/mongo/"]):
        raise Exception("ESLint errors")

    import buildscripts.clang_format
    if not buildscripts.clang_format.lint_all(None):
        raise Exception("clang-format lint errors")

    import buildscripts.pylinters
    buildscripts.pylinters.lint_all(None, {}, [])

    import buildscripts.lint
    if not buildscripts.lint.run_lint( [ "src/mongo/" ] ):
        raise Exception( "lint errors" )

env.Alias( "lint" , [] , [ doLint ] )
env.AlwaysBuild( "lint" )


#  ----  INSTALL -------

def getSystemInstallName():
    arch_name = env.subst('$MONGO_DISTARCH')

    n = arch_name

    if len(mongo_modules):
            n += "-" + "-".join(m.name for m in mongo_modules)

    dn = env.subst('$MONGO_DISTMOD')
    if len(dn) > 0:
        n = n + "-" + dn

    return n

# This function will add the version.txt file to the source tarball
# so that versioning will work without having the git repo available.
def add_version_to_distsrc(env, archive):
    version_file_path = env.subst("$MONGO_DIST_SRC_PREFIX") + "version.json"
    if version_file_path not in archive:
        version_data = {
            'version': env['MONGO_VERSION'],
            'githash': env['MONGO_GIT_HASH'],
        }
        archive.append_file_contents(
            version_file_path,
            json.dumps(
                version_data,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )
        )

env.AddDistSrcCallback(add_version_to_distsrc)

env['SERVER_DIST_BASENAME'] = env.subst('mongodb-%s-$MONGO_DISTNAME' % (getSystemInstallName()))

module_sconscripts = moduleconfig.get_module_sconscripts(mongo_modules)

# The following symbols are exported for use in subordinate SConscript files.
# Ideally, the SConscript files would be purely declarative.  They would only
# import build environment objects, and would contain few or no conditional
# statements or branches.
#
# Currently, however, the SConscript files do need some predicates for
# conditional decision making that hasn't been moved up to this SConstruct file,
# and they are exported here, as well.
Export("get_option")
Export("has_option")
Export("serverJs")
Export("usemozjs")
Export('module_sconscripts')
Export("debugBuild optBuild")
Export("wiredtiger")
Export("mmapv1")
Export("mobile_se")
Export("endian")
Export("ssl_provider")
Export("free_monitoring")

def injectMongoIncludePaths(thisEnv):
    thisEnv.AppendUnique(CPPPATH=['$BUILD_DIR'])
env.AddMethod(injectMongoIncludePaths, 'InjectMongoIncludePaths')

def injectModule(env, module, **kwargs):
    injector = env['MODULE_INJECTORS'].get(module)
    if injector:
        return injector(env, **kwargs)
    return env
env.AddMethod(injectModule, 'InjectModule')

compileCommands = env.CompilationDatabase('compile_commands.json')
compileDb = env.Alias("compiledb", compileCommands)

# Microsoft Visual Studio Project generation for code browsing
vcxprojFile = env.Command(
    "mongodb.vcxproj",
    compileCommands,
    r"$PYTHON buildscripts\make_vcxproj.py mongodb")
vcxproj = env.Alias("vcxproj", vcxprojFile)

distSrc = env.DistSrc("mongodb-src-${MONGO_VERSION}.tar")
env.NoCache(distSrc)
env.Alias("distsrc-tar", distSrc)

distSrcGzip = env.GZip(
    target="mongodb-src-${MONGO_VERSION}.tgz",
    source=[distSrc])
env.NoCache(distSrcGzip)
env.Alias("distsrc-tgz", distSrcGzip)

distSrcZip = env.DistSrc("mongodb-src-${MONGO_VERSION}.zip")
env.NoCache(distSrcZip)
env.Alias("distsrc-zip", distSrcZip)

env.Alias("distsrc", "distsrc-tgz")

# Defaults for SCons provided flags. SetOption only sets the option to our value
# if the user did not provide it. So for any flag here if it's explicitly passed
# the values below set with SetOption will be overwritten.
#
# Default j to the number of CPUs on the system. Note: in containers this
# reports the number of CPUs for the host system. We're relying on the standard
# library here and perhaps in a future version of Python it will instead report
# the correct number when in a container.
try:
    env.SetOption('num_jobs', multiprocessing.cpu_count())
# On some platforms (like Windows) on Python 2.7 multiprocessing.cpu_count
# is not implemented. After we upgrade to Python 3.4+ we can use alternative
# methods that are cross-platform.
except NotImplementedError:
    pass


# Do this as close to last as possible before reading SConscripts, so
# that any tools that may have injected other things via emitters are included
# among the side effect adornments.
#
# TODO: Move this to a tool.
if has_option('jlink'):
    jlink = get_option('jlink')
    if jlink <= 0:
        env.FatalError("The argument to jlink must be a positive integer or float")
    elif jlink < 1 and jlink > 0:
        jlink = env.GetOption('num_jobs') * jlink
        jlink = round(jlink)
        if jlink < 1.0:
            print("Computed jlink value was less than 1; Defaulting to 1")
            jlink = 1.0

    jlink = int(jlink)
    target_builders = ['Program', 'SharedLibrary', 'LoadableModule']

    # A bound map of stream (as in stream of work) name to side-effect
    # file. Since SCons will not allow tasks with a shared side-effect
    # to execute concurrently, this gives us a way to limit link jobs
    # independently of overall SCons concurrency.
    jlink_stream_map = dict()

    def jlink_emitter(target, source, env):
        name = str(target[0])
        se_name = "#jlink-stream" + str(hash(name) % jlink)
        se_node = jlink_stream_map.get(se_name, None)
        if not se_node:
            se_node = env.Entry(se_name)
            # This may not be necessary, but why chance it
            env.NoCache(se_node)
            jlink_stream_map[se_name] = se_node
        env.SideEffect(se_node, target)
        return (target, source)

    for target_builder in target_builders:
        builder = env['BUILDERS'][target_builder]
        base_emitter = builder.emitter
        new_emitter = SCons.Builder.ListEmitter([base_emitter, jlink_emitter])
        builder.emitter = new_emitter

# Keep this late in the game so that we can investigate attributes set by all the tools that have run.
if has_option("cache"):
    if get_option("cache") == "nolinked":
        def noCacheEmitter(target, source, env):
            for t in target:
                try:
                    if getattr(t.attributes, 'thin_archive', False):
                        continue
                except(AttributeError):
                    pass
                env.NoCache(t)
            return target, source

        def addNoCacheEmitter(builder):
            origEmitter = builder.emitter
            if SCons.Util.is_Dict(origEmitter):
                for k,v in origEmitter:
                    origEmitter[k] = SCons.Builder.ListEmitter([v, noCacheEmitter])
            elif SCons.Util.is_List(origEmitter):
                origEmitter.append(noCacheEmitter)
            else:
                builder.emitter = SCons.Builder.ListEmitter([origEmitter, noCacheEmitter])

        addNoCacheEmitter(env['BUILDERS']['Program'])
        addNoCacheEmitter(env['BUILDERS']['StaticLibrary'])
        addNoCacheEmitter(env['BUILDERS']['SharedLibrary'])
        addNoCacheEmitter(env['BUILDERS']['LoadableModule'])

env.SConscript(
    dirs=[
        'src',
    ],
    duplicate=False,
    exports=[
        'env',
    ],
    variant_dir='$BUILD_DIR',
)

all = env.Alias('all', ['core', 'tools', 'dbtest', 'unittests', 'integration_tests', 'benchmarks'])

# run the Dagger tool if it's installed
if should_dagger:
    dependencyDb = env.Alias("dagger", env.Dagger('library_dependency_graph.json'))
    # Require everything to be built before trying to extract build dependency information
    env.Requires(dependencyDb, all)

# We don't want installing files to cause them to flow into the cache,
# since presumably we can re-install them from the origin if needed.
env.NoCache(env.FindInstalledFiles())

# Declare the cache prune target
cachePrune = env.Command(
    target="#cache-prune",
    source=[
        "#buildscripts/scons_cache_prune.py",
    ],
    action="$PYTHON ${SOURCES[0]} --cache-dir=${CACHE_DIR.abspath} --cache-size=${CACHE_SIZE} --prune-ratio=${CACHE_PRUNE_TARGET/100.00}",
    CACHE_DIR=env.Dir(cacheDir),
)

env.AlwaysBuild(cachePrune)
env.Alias('cache-prune', cachePrune)

# Substitute environment variables in any build targets so that we can
# say, for instance:
#
# > scons --prefix=/foo/bar '$INSTALL_DIR'
# or
# > scons \$BUILD_DIR/mongo/base
#
# That way, you can reference targets under the variant dir or install
# path via an invariant name.
#
# We need to replace the values in the BUILD_TARGETS object in-place
# because SCons wants it to be a particular object.
for i, s in enumerate(BUILD_TARGETS):
    BUILD_TARGETS[i] = env.subst(s)
