#!/bin/bash

set -o nounset
set -o errexit

GALAXY_VENV=${GALAXY_VENV:-/var/lib/galaxy/venv}

mkdir -p build/static

NODE_PATH=/tmp/node_modules/ /tmp/node_modules/.bin/gulp build

${GALAXY_VENV}/bin/python manage.py collectstatic --noinput --clear
