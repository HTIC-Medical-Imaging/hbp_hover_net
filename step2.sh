#! bash

BIOSAMPLEID=$1
SECNO=$2
INPUTJP2_DIR=$3
OUTPUT_DIR=$4
CACHE_PATH=$5
N_INF_WORKERS=$6
N_PP_WORKERS=$7
BATCH_SIZE=$8
GPU_LIST=$9

JP2CACHE_DIR='${CACHE_PATH}/special/jp2cache'
MODEL_PATH=/workspace/weights/hovernet_fast_pannuke_type_tf2pytorch.tar

INPUT_JP2=`ls ${INPUTJP2_DIR}/B_${BIOSAMPLEID}_*_${SECNO}_lossless.jp2|head -1`
BASENM=`basename $INPUT_JP2`

python run_infer.py --gpu=$GPU_LIST --nr_types=6 --type_info_path=type_info.json --batch_size=$BATCH_SIZE --model_mode=fast --model_path=$MODEL_PATH  --nr_inference_workers=$N_INF_WORKERS --nr_post_proc_workers=$N_PP_WORKERS \
    wsi --proc_mag=20 --input_dir=$JP2CACHE_DIR --basename=$BASENM --output_dir=$OUTPUT_DIR --cache_path=$CACHE_PATH --chunk_shape=16400 --save_mask  --save_thumb # --debug