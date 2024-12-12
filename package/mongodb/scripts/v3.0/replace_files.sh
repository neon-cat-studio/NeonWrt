#!/bin/sh

if [ $# -ne 1 ]
then
    echo "Please specitify MongoDB Build Directory"
    exit 0;
fi

_MongoDB_Build_Dir=$1

rm -rf $_MongoDB_Build_Dir/SConstruct; \
cp ./files/v3.0/SConstruct.py \
	$_MongoDB_Build_Dir/SConstruct; \

rm -rf $_MongoDB_Build_Dir/src/mongo/SConscript; \
cp ./files/v3.0/src/mongo/SConscript.py \
	$_MongoDB_Build_Dir/src/mongo/SConscript; \

rm -rf $_MongoDB_Build_Dir/src/third_party/SConscript; \
rm -rf $_MongoDB_Build_Dir/src/third_party/v8-3.25/SConscript; \
rm -rf $_MongoDB_Build_Dir/src/third_party/gperftools-2.2/SConscript; \
rm -rf $_MongoDB_Build_Dir/src/third_party/s2/SConscript; \
rm -rf $_MongoDB_Build_Dir/src/third_party/s2/base/SConscript; \
rm -rf $_MongoDB_Build_Dir/src/third_party/s2/strings/SConscript; \
rm -rf $_MongoDB_Build_Dir/src/third_party/s2/util/coding/SConscript; \
rm -rf $_MongoDB_Build_Dir/src/third_party/s2/util/math/SConscript; \

cp ./files/v3.0/src/third_party/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/SConscript; \
cp ./files/v3.0/src/third_party/gperftools-2.2/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/gperftools-2.2/SConscript; \
cp ./files/v3.0/src/third_party/s2/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/s2/SConscript; \
cp ./files/v3.0/src/third_party/s2/base/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/s2/base/SConscript; \
cp ./files/v3.0/src/third_party/s2/strings/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/s2/strings/SConscript; \
cp ./files/v3.0/src/third_party/s2/util/coding/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/s2/util/coding/SConscript; \
cp ./files/v3.0/src/third_party/s2/util/math/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/s2/util/math/SConscript; \
cp ./files/v3.0/src/third_party/v8-3.25/SConscript.py \
	$_MongoDB_Build_Dir/src/third_party/v8-3.25/SConscript; \