#!/bin/bash
#
# Removes containers and images associated with the app.
#
# By default will remove all containers and images.
# Pass 'container' to only remove containers. 
# Pass 'images' to remove images only.
#

if [ $# -eq 0 ] || [ "$1" = "containers" ]; then
    echo "Removing Galaxy containers..."
    containers=$(docker ps -a --format "{{.Names}}" | \
    grep -e django \
         -e elastic \
         -e postgres \
         -e rabbit \
         -e memcache \
         -e gulp \
         -e ansible_ansible-container_1 | wc -l | tr -d '[[:space:]]')
    if [ ${containers} -gt 0 ]; then 
        docker rm --force $(docker ps -a --format "{{.Names}}" | \
          grep -e django -e elastic -e postgres -e rabbit -e memcache -e gulp -e ansible_ansible-container_1)
    else
        echo "No Galaxy containers found"
    fi
fi

if [ $# -eq 0 ] || [ "$1" = "images" ]; then
    echo "Removing Galaxy images..."
    images=$(docker images -a --format "{{.Repository}}:{{.Tag}}" | grep galaxy | wc -l | tr -d '[[:space:]]')
    if [ ${images} -gt 0 ]; then
        docker rmi --force $(docker images -a --format "{{.Repository}}:{{.Tag}}" | grep galaxy)
    else
        echo "No Galaxy images found"
    fi
fi

