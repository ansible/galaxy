#!/bin/bash

set -o nounset
set -o errexit

readonly GALAXY_VENV=${GALAXY_VENV:-/usr/share/galaxy/venv}

# shellcheck disable=SC2034
VIRTUAL_ENV_DISABLE_PROMPT=1
# shellcheck disable=SC1090
source "${GALAXY_VENV}/bin/activate"

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
