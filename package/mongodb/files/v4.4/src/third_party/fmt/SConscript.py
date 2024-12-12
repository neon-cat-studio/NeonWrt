# -*- mode: python -*-
Import("env")
Import("has_option")
Import("debugBuild")
env = env.Clone()

# In libfmt 6.1.1, when compiling format.cc, this is needed for function fmt::v6::internal::report_error()

env.AppendUnique(CXXFLAGS=['-Wno-error=unused-result'])

env.Library(
    target='fmt',
    source=env.File([
        'format.cc',
        'posix.cc',
    ], 'dist/src'))

