#!/bin/sh

# how we got the last firefox sources

MOZJS_VERSION=60.3.0
MOZJS_VERSION_ESR=60.3.0esr
MOZJS_SOURCE=firefox-$MOZJS_VERSION_ESR.source.tar.xz

if [ ! -f $MOZJS_SOURCE ]
then
    curl -O "https://ftp.mozilla.org/pub/mozilla.org/firefox/releases/$MOZJS_VERSION_ESR/source/$MOZJS_SOURCE"
fi

if [ ! -d ./mozilla-release ]
then
    xzcat $MOZJS_SOURCE | tar -xf-
    mv firefox-$MOZJS_VERSION mozilla-release
fi
