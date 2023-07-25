#! /usr/bin/bash

scriptname=$1
shift

echo "entry point->" ${scriptname}

eval $scriptname $@

echo "ended."
if [ $keepalive == 1 ]
then
    echo "keepalive"
    tail -f /dev/null
fi