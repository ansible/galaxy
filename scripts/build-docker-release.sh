#!/bin/bash

set -o nounset
set -o errexit

docker build --rm -t galaxy-build -f scripts/docker-release/Dockerfile.build .
docker run --rm -v $(pwd):/galaxy galaxy-build

# TODO(cutwater): Move as a separate build step to Makefile
docker build --rm -t galaxy \
    -f scripts/docker-release/Dockerfile .
