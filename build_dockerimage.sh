version=$1
docker build --rm -t hbp1/hovernet_mmap:$version -f ./Dockerfile ./dist
