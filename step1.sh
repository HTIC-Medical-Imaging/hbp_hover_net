#! /usr/bin/bash

BIOSAMPLEID=$1
SECNO=$2
INPUTJP2_DIR=$3
OUTPUT_DIR=$4
CACHE_PATH=$5

JP2CACHE_DIR=${CACHE_PATH}'/special/jp2cache'

INPUT_JP2=`ls ${INPUTJP2_DIR}/B_${BIOSAMPLEID}_*_${SECNO}_lossless.jp2|head -1`
mkdir -p $JP2CACHE_DIR
python create_mmap.py $INPUT_JP2 $JP2CACHE_DIR