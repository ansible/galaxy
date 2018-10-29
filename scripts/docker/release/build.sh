#!/bin/bash

set -o nounset
set -o errexit

readonly VENV_BIN=${VENV_BIN:-/var/lib/galaxy/venv/bin}

# shellcheck disable=SC2034
VIRTUAL_ENV_DISABLE_PROMPT=1
# shellcheck disable=SC1090
source "${VENV_BIN}/activate"

mkdir -p /galaxy/build/ \
         /galaxy/dist/

pushd /galaxy/galaxyui

yarn install
yarn run ng build --prod --output-path /galaxy/build/static

popd

# TODO(cutwater): Use make commands for build
python setup.py --version > /galaxy/dist/VERSION
python setup.py bdist_wheel
python manage.py collectstatic --noinput

# Build docs
pushd /galaxy/docs/docsite/
make docs
popd

mkdir /galaxy/build/static/docs
rsync -av /galaxy/docs/docsite/_build/html/ /galaxy/build/static/docs
