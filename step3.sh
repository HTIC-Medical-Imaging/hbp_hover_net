#! bash

BIOSAMPLEID=$1
SECNO=$2
INPUTJP2_DIR=$3
OUTPUT_DIR=$4

DT=`date +%y%h%d_%H%M`
ALGO='hover_net'
VER='v1'

INPUT_JP2=`ls ${INPUTJP2_DIR}/B_${BIOSAMPLEID}_*_${SECNO}_lossless.jp2|head -1`
BASENM=`basename $INPUT_JP2`

python setup_db.py $BIOSAMPLEID $SECNO $ALGO $VER $BASENM $DT

python insert_db_records.py $BIOSAMPLEID $SECNO $OUTPUT_DIR $BASENM $DT