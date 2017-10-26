#!/bin/bash

set -o nounset
set -o errexit
set -o pipefail

source /setup/common.sh

init_django_db

exec /venv/bin/gunicorn -w 2 -b 0.0.0.0:8000 galaxy.wsgi:application
