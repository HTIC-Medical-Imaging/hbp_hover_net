
VER?=v1a

dist:
    ./build_dist.sh

docker: dist
    ./build_dockerimage.sh $(VER) && ./test_build_dockercontainer.sh $(VER)

test: docker
    docker start test_$(VER) && docker exec -it test_$(VER) bash

