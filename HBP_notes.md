
CELL DETECTION with hover_net
---
docker rmi hovernet_mmap:v1
		
docker build --rm -t "hovernet_mmap:v1" .

docker run -it --rm --gpus all --ipc=host --ulimit memlock=-1 -v /raid/keerthi/data:/data -v /raid/keerthi/cache:/cache hovernet_mmap:v1 /workspace/run_wsi_mmap.sh /data/special/jp2cache/B_37_FB3-SL_570-ST_NISL-SE_1708_lossless.jp2 /data/output /cache 1 32 192 0,1,2,3,4,5,6,7


POSTGIS db
---
docker pull postgis/postgis:15-3.3

docker run --name dbpostgis -p 5432:5432 -e POSTGRES_PASSWORD=whatever \
-e PGDATA=/var/lib/postgresql/data/pgdata \
	-v /raid/keerthi/dbdata:/var/lib/postgresql/data \
	-d postgis/postgis:15-3.3
