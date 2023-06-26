INPUT_JP2=$1
OUTPUT_DIR=$2
MODEL_DIR=$3
N_INF_WORKERS=$4
N_PP_WORKERS=$5
INPUT_DIR=`dirname $INPUT_JP2`

python create_mmap.py $INPUT_JP2 $INPUT_DIR

python run_infer.py \
--gpu='0,1,2,3,4,5,6,7' \
--nr_types=6 \
--type_info_path=type_info.json \
--batch_size=2 \
--model_mode=fast \
--model_path=$MODEL_DIR/hovernet_fast_pannuke_type_tf2pytorch.tar \
--nr_inference_workers=$N_INF_WORKERS \
--nr_post_proc_workers=$N_PP_WORKERS \
wsi \
--input_dir=$INPUT_DIR \
--output_dir=$OUTPUT_DIR \
--chunk_shape=16400