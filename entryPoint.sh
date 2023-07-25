#! /usr/bin/bash

scriptname=$1
keepalive=${@: -1}

eval $scriptname $@

if [ $keepalive == 1 ]
then
    tail -f /dev/null
fi