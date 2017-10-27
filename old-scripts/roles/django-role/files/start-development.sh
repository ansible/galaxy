#!/bin/bash

set -o nounset
set -o errexit
set -o pipefail

source /setup/common.sh

init_django_db

exec /venv/bin/python /galaxy/manage.py runserver 0.0.0.0:8000 --nostatic
