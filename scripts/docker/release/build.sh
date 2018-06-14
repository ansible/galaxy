#!/bin/bash

set -o nounset
set -o errexit

readonly VENV_BIN=${VENV_BIN:-/var/lib/galaxy/venv/bin}

VIRTUAL_ENV_DISABLE_PROMPT=1
source ${VENV_BIN}/activate

mkdir -p /galaxy/build/ \
         /galaxy/dist/

pushd /galaxy/galaxyui

yarn install
yarn run ng build --prod --output-path /galaxy/build/static

popd

# TODO(cutwater): Use make commands for build
${VENV_BIN}/python setup.py --version > /galaxy/dist/VERSION
${VENV_BIN}/python setup.py bdist_wheel
${VENV_BIN}/python manage.py collectstatic --noinput
