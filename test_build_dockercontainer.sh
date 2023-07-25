version=$1
docker stop test_$version && docker rm test_$version
docker create --name test_$version --ipc=host --gpus all -v /raid/keerthi/data:/data -v /raid/keerthi/cache:/cache -e keepalive=1 -e POSTGRES_HOST=172.17.0.2 hbp1/hovernet_mmap:$version /workspace/entryPoint.sh echo "nop"