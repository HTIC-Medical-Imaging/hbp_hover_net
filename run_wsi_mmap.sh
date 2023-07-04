INPUT_JP2=$1
OUTPUT_DIR=$2
CACHE_PATH=$3
MODEL_PATH=/workspace/weights/hovernet_fast_pannuke_type_tf2pytorch.tar
N_INF_WORKERS=$4
N_PP_WORKERS=$5
BATCH_SIZE=$6
GPU_LIST=$7
INPUT_DIR=`dirname $INPUT_JP2`

python create_mmap.py $INPUT_JP2 $INPUT_DIR && python run_infer.py --gpu=$GPU_LIST --nr_types=6 --type_info_path=type_info.json --batch_size=$BATCH_SIZE --model_mode=fast --model_path=$MODEL_PATH  --nr_inference_workers=$N_INF_WORKERS --nr_post_proc_workers=$N_PP_WORKERS \
    wsi --proc_mag=20 --input_dir=$INPUT_DIR --output_dir=$OUTPUT_DIR --cache_path=$CACHE_PATH --chunk_shape=16400 --save_mask  --save_thumb --debug
