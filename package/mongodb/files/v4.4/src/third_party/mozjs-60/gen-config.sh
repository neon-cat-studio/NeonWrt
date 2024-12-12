#!/bin/sh

set -e
set -v
set -x

if [ $# -ne 2 ]
then
    echo "Please supply an arch: x86_64, i386, etc and toolchain prefix"
    exit 0;
fi

_TARGET_ARCH=$1
_TOOLCHAIN_PREFIX=$2
_Path=platform/$_TARGET_ARCH/linux

# the two files we need are js-confdefs.h which get used for the build and
# js-config.h for library consumers.  We also get different unity source files
# based on configuration, so save those too.

cd mozilla-release/js/src
rm config.cache || true

PYTHON=python ./configure \
	--without-intl-api \
	--enable-posix-nspr-emulation \
	--disable-trace-logging \
	--disable-js-shell \
	--disable-tests \
	--enable-compile-environment \
	--with-toolchain-prefix=$_TOOLCHAIN_PREFIX \
	--host=x86_64-linux \
	--target=$_TARGET_ARCH-linux

make recurse_export

cd ../../..

rm -rf $_Path/

mkdir -p $_Path/build
mkdir $_Path/include

cp mozilla-release/js/src/js/src/js-confdefs.h $_Path/build
cp mozilla-release/js/src/js/src/*.cpp $_Path/build
cp mozilla-release/js/src/js/src/js-config.h $_Path/include

for unified_file in $(ls -1 $_Path/build/*.cpp) ; do
	sed 's/#include ".*\/js\/src\//#include "/' < $unified_file > t1
	sed 's/#error ".*\/js\/src\//#error "/' < t1 > $unified_file
	rm t1
done


