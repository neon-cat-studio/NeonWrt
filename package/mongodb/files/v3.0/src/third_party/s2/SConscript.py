# -*- mode: python -*-

Import("env")

env = env.Clone()

env.SConscript( [
	"base/SConscript",
	"strings/SConscript",
	"util/coding/SConscript",
	"util/math/SConscript",
        ], exports={ 'env' : env })

env.Append(CCFLAGS=['-DDEBUG_MODE=false'])

env.Library( "s2",
    [ 
	"s1angle.cc",
	"s2.cc",
	"s2cellid.cc",
	"s2latlng.cc",
	"s1interval.cc",
	"s2cap.cc",
	"s2cell.cc",
	"s2cellunion.cc",
	"s2edgeindex.cc",
	"s2edgeutil.cc",
	"s2latlngrect.cc",
	"s2loop.cc",
	"s2pointregion.cc",
	"s2polygon.cc",
	"s2polygonbuilder.cc",
	"s2polyline.cc",
	"s2r2rect.cc",
	"s2region.cc",
	"s2regioncoverer.cc",
	"s2regionintersection.cc",
	"s2regionunion.cc",
    ], LIBDEPS=['$BUILD_DIR/third_party/s2/base/base',
		'$BUILD_DIR/third_party/s2/strings/strings',
		'$BUILD_DIR/third_party/s2/util/coding/coding',
		'$BUILD_DIR/third_party/s2/util/math/math'])

#env.Program('r1interval_test', ['r1interval_test.cc'],
#            LIBDEPS=['s2', '$BUILD_DIR/third_party/gtest/gtest_with_main'])
#env.Program('s1angle_test', ['s1angle_test.cc'],
#            LIBDEPS=['s2', '$BUILD_DIR/third_party/gtest/gtest_with_main'])
#env.Program('s1interval_test', ['s1interval_test.cc'],
#            LIBDEPS=['s2', '$BUILD_DIR/third_party/gtest/gtest_with_main'])
#env.Program('s2regioncoverer_test', ['s2regioncoverer_test.cc'],
#            LIBDEPS=['s2', '$BUILD_DIR/third_party/gtest/gtest_with_main'])
#env.Program('s2_test', ['s2_test.cc'],
#            LIBDEPS=['s2', '$BUILD_DIR/third_party/gtest/gtest_with_main'])
