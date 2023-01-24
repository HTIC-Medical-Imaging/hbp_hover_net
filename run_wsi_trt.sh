
python run_infer.py \
--gpu='0,1,2,3,4,5,6,7' \
--nr_types=6 \
--type_info_path=type_info.json \
--batch_size=64 \
--model_mode=fast \
--model_path='hovernet_256_64_best.plan' \
--nr_inference_workers=36 \
--nr_post_proc_workers=36 \
wsi \
--input_dir=dataset/sample_wsis/img/ \
--output_dir=dataset/sample_wsis/out/ \

