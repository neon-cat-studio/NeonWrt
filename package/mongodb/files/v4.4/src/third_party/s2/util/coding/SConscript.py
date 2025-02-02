# -*- mode: python -*-

Import("env")

env = env.Clone()

env.Append(CCFLAGS=['-Isrc/third_party/s2'])
env.Append(CCFLAGS=['-Isrc/third_party/gflags-2.0/src'])

env.Library(
    "coding",
    [ 
	"coder.cc",
	"varint.cc",
    ],
    LIBDEPS=[
        '$BUILD_DIR/mongo/base',
        '$BUILD_DIR/third_party/s2/base/base_s2',
    ])
