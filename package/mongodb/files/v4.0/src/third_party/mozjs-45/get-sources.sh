#!/bin/sh

# how we got the last firefox sources

MOZJS_VERSION=45.9.0esr
MOZJS_SOURCE=firefox-$MOZJS_VERSION.source.tar.xz

if [ ! -f $MOZJS_SOURCE ]
then
    curl -O "https://ftp.mozilla.org/pub/mozilla.org/firefox/releases/$MOZJS_VERSION/source/$MOZJS_SOURCE"
fi

if [ ! -d ./mozilla-release ]
then
    xzcat $MOZJS_SOURCE | tar -xf-
    mv firefox-$MOZJS_VERSION mozilla-release
fi
