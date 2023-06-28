
docker rmi hovernet_mmap:v1
		
docker build --rm -t "hovernet_mmap:v1" .

docker run -it --rm --gpus all --ipc=host --ulimit memlock=-1 -v /raid/keerthi/data:/data -v /raid/keerthi/cache:/cache hovernet_mmap:v1 /workspace/run_wsi_mmap.sh /data/special/jp2cache/B_37_FB3-SL_570-ST_NISL-SE_1708_lossless.jp2 /data/output /cache 32 32 64 0,1