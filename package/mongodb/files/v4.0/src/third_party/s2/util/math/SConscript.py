# -*- mode: python -*-

Import("env")

env = env.Clone()

env.Append(CCFLAGS=['-Isrc/third_party/s2'])
env.Append(CCFLAGS=['-Isrc/third_party/gflags-2.0/src'])

env.Library("math",
          [ "mathutil.cc",
           # "mathlimits.cc",
          ],
          LIBDEPS=[
              '$BUILD_DIR/mongo/base',
              '$BUILD_DIR/third_party/s2/base/base_s2',
          ])
