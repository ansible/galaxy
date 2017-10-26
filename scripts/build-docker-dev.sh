#!/bin/bash

set -o nounset
set -o errexit

docker build --rm -t galaxy-build -f scripts/docker-release/Dockerfile.build .

docker build --rm -t galaxy-dev -f scripts/docker-dev/Dockerfile .

