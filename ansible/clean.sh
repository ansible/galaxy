#!/bin/bash
#
# Removes all containers and images associated with the app 
#

echo "Removing all Galaxy containers and images..."

containers=$(docker ps -a --format "{{.Names}}" | grep -e django -e elastic -e postgres -e rabbit -e memcache -e gulp | wc -l | tr -d '[[:space:]]')
if [ ${containers} -gt 0 ]; then 
    docker rm --force $(docker ps -a --format "{{.Names}}" | grep -e django -e elastic -e postgres -e rabbit -e memcache -e gulp)
else
    echo "No Galaxy containers found"
fi

images=$(docker images -a --format "{{.Repository}}:{{.Tag}}" | grep galaxy | wc -l | tr -d '[[:space:]]')
if [ ${images} -gt 0 ]; then
    docker rmi --force $(docker images -a --format "{{.Repository}}:{{.Tag}}" | grep galaxy)
else
    echo "No Galaxy images found"
fi

rm -rf ~/.galaxy
