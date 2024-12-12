#!/bin/sh

if [ $# -ne 1 ]
then
    echo "Please specitify MongoDB Build Directory"
    exit 0;
fi

_MongoDB_Build_Dir=$1

rm -rf $_MongoDB_Build_Dir/etc/pip/dev-requirements.txt
cp ./files/v4.4/etc/pip/dev-requirements.txt \
	$_MongoDB_Build_Dir/etc/pip/dev-requirements.txt

rm -rf $_MongoDB_Build_Dir/site_scons/mongo/toolchain.py
rm -rf $_MongoDB_Build_Dir/site_scons/site_tools/icecream.py
rm -rf $_MongoDB_Build_Dir/site_scons/site_tools/incremental_link.py
rm -rf $_MongoDB_Build_Dir/site_scons/site_tools/mongo_benchmark.py
rm -rf $_MongoDB_Build_Dir/site_scons/site_tools/separate_debug.py
cp ./files/v4.4/site_scons/mongo/toolchain.py \
	$_MongoDB_Build_Dir/site_scons/mongo/toolchain.py
cp ./files/v4.4/site_scons/site_tools/icecream.py \
	$_MongoDB_Build_Dir/site_scons/site_tools/icecream.py
cp ./files/v4.4/site_scons/site_tools/incremental_link.py \
	$_MongoDB_Build_Dir/site_scons/site_tools/incremental_link.py
cp ./files/v4.4/site_scons/site_tools/mongo_benchmark.py \
	$_MongoDB_Build_Dir/site_scons/site_tools/mongo_benchmark.py
cp ./files/v4.4/site_scons/site_tools/separate_debug.py \
	$_MongoDB_Build_Dir/site_scons/site_tools/separate_debug.py; \

rm -rf $_MongoDB_Build_Dir/SConstruct
rm -rf $_MongoDB_Build_Dir/src/SConscript
cp ./files/v4.4/SConstruct.py \
	$_MongoDB_Build_Dir/SConstruct
cp ./files/v4.4/src/SConscript.py \
	$_MongoDB_Build_Dir/src/SConscript

rm -rf $_MongoDB_Build_Dir/src/mongo/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/base/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/client/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/db/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/db/ftdc/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/db/query/collation/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/dbtests/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/embedded/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/embedded/mongo_embedded/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/embedded/mongoc_embedded/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/stdx/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/util/SConscript
rm -rf $_MongoDB_Build_Dir/src/mongo/util/net/SConscript
cp ./files/v4.4/src/mongo/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/SConscript
cp ./files/v4.4/src/mongo/base/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/base/SConscript
cp ./files/v4.4/src/mongo/client/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/client/SConscript
cp ./files/v4.4/src/mongo/db/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/db/SConscript
cp ./files/v4.4/src/mongo/db/ftdc/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/db/ftdc/SConscript
cp ./files/v4.4/src/mongo/db/query/collation/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/db/query/collation/SConscript
cp ./files/v4.4/src/mongo/dbtests/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/dbtests/SConscript
cp ./files/v4.4/src/mongo/embedded/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/embedded/SConscript
cp ./files/v4.4/src/mongo/embedded/mongo_embedded/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/embedded/mongo_embedded/SConscript
cp ./files/v4.4/src/mongo/embedded/mongoc_embedded/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/embedded/mongoc_embedded/SConscript
cp ./files/v4.4/src/mongo/stdx/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/stdx/SConscript
cp ./files/v4.4/src/mongo/util/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/util/SConscript
cp ./files/v4.4/src/mongo/util/net/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/util/net/SConscript

rm -rf $_MongoDB_Build_Dir/src/third_party/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/fmt/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/icu4c-57.1/source/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/IntelRDFPMathLib20U1/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/kms-message/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/mozjs-60/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/mozjs-60/get-sources.sh
rm -rf $_MongoDB_Build_Dir/src/third_party/mozjs-60/gen-config.sh
rm -rf $_MongoDB_Build_Dir/src/third_party/s2/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/s2/util/coding/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/s2/util/math/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/timelib-2018.01/SConscript
rm -rf $_MongoDB_Build_Dir/src/third_party/wiredtiger/SConscript
cp ./files/v4.4/src/third_party/SConscript.py  \
	$_MongoDB_Build_Dir/src/third_party/SConscript
cp ./files/v4.4/src/third_party/fmt/SConscript.py  \
	$_MongoDB_Build_Dir/src/third_party/fmt/SConscript
cp ./files/v4.4/src/third_party/icu4c-57.1/source/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/icu4c-57.1/source/SConscript
cp ./files/v4.4/src/third_party/IntelRDFPMathLib20U1/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/IntelRDFPMathLib20U1/SConscript
cp ./files/v4.4/src/third_party/kms-message/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/kms-message/SConscript
cp ./files/v4.4/src/third_party/mozjs-60/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/mozjs-60/SConscript
cp ./files/v4.4/src/third_party/mozjs-60/get-sources.sh \
	$_MongoDB_Build_Dir/src/third_party/mozjs-60/get-sources.sh
cp ./files/v4.4/src/third_party/mozjs-60/gen-config.sh \
	$_MongoDB_Build_Dir/src/third_party/mozjs-60/gen-config.sh
cp ./files/v4.4/src/third_party/s2/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/s2/SConscript
cp ./files/v4.4/src/third_party/s2/util/coding/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/s2/util/coding/SConscript
cp ./files/v4.4/src/third_party/s2/util/math/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/s2/util/math/SConscript
cp ./files/v4.4/src/third_party/timelib-2018.01/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/timelib-2018.01/SConscript
cp ./files/v4.4/src/third_party/wiredtiger/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/wiredtiger/SConscript