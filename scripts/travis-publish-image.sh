#!/bin/bash

set -o xtrace

readonly GALAXY_VERSION_TAG="^v[0-9]"

if [[ "$TRAVIS_PULL_REQUEST" != "false" ]]; then
    echo "WARNING: Build trgiggered by pull request. Skipping docker image build."
    exit 0
fi


if [[ "$TRAVIS_BRANCH" == "develop" ]]; then
    docker tag galaxy:latest ansible/galaxy:develop
    docker login --username "$DOCKER_USERNAME" --password "$DOCKER_PASSWORD"
    echo "Pushing docker image: ansible/galaxy:develop"
    docker push ansible/galaxy:develop
elif [[ "$TRAVIS_TAG" =~ $GALAXY_VERSION_TAG ]]; then
    # Strip 'v' prefix from git tag
    IMAGE_TAG=${TRAVIS_TAG#v}

    docker tag galaxy:latest "ansible/galaxy:$IMAGE_TAG"
    docker tag galaxy:latest ansible/galaxy:latest

    docker login --username "$DOCKER_USERNAME" --password "$DOCKER_PASSWORD"
    echo "Pushing docker image: ansible/galaxy:$IMAGE_TAG"
    docker push ansible/galaxy:$IMAGE_TAG
    echo "Updating ansible/galaxy:latest to ansible/galaxy:$IMAGE_TAG"
    docker push ansible/galaxy:latest
else
    echo "WARNING: Cannot publish image. Configuration not supported."
    exit 0
fi
