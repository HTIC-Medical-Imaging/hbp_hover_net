#! /usr/bin/bash

scriptname=$1
keepalive=${@: -1}

eval $scriptname $@

if [ -t $keepalive ]
    tail -f /dev/null
fi