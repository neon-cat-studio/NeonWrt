#!/bin/sh

if [ $# -ne 1 ]
then
    echo "Please supply an arch: x86_64, i386, etc"
    exit 0;
fi

_Path=platform/$1/linux

_TARGET_ARCH=$1
_CONFIG_OPTS="--host=$_TARGET_ARCH-linux --target=$_TARGET_ARCH-linux-gnueabihf --build=x86_64-linux"

# the two files we need are js-confdefs.h which get used for the build and
# js-config.h for library consumers.  We also get different unity source files
# based on configuration, so save those too.

cd mozilla-release/js/src
rm config.cache

PYTHON=python ./configure --enable-jemalloc=no --without-intl-api --enable-posix-nspr-emulation --disable-trace-logging "$_CONFIG_OPTS"

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
