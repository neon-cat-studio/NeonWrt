#!/usr/bin/env bash

# Determine the script name or default argument
case "${0##*/}" in
    pywrap.sh) arg1="";;
    *) arg1="$0.py" ;;
esac

# Search for a Python 3 interpreter
for bin in python3 python; do
    case "$($bin --version 2>&1)" in
        "Python 3"*) exec $bin $arg1 "$@" ;;
    esac
done

# If no Python 3 interpreter is found, output an error
echo "Unable to find a Python 3.x interpreter for executing ${arg1:+$arg1 }$@ !" >&2
exit 1
