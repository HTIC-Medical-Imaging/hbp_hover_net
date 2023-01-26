python run_infer.py \
--gpu='0,1,2,3,4,5,6,7' \
--nr_types=6 \
--type_info_path=type_info.json \
--batch_size=128 \
--model_mode=fast \
--model_path=../hovernet_fast_pannuke_type_tf2pytorch.tar \
--nr_inference_workers=32 \
--nr_post_proc_workers=64 \
wsi \
--input_dir=dataset/sample_wsis/img/ \
--output_dir=dataset/sample_wsis/out/ \
--chunk_shape=16400