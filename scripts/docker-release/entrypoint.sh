#!/bin/bash

set -o nounset
set -o errexit

readonly VENV_BIN=${VENV_BIN:-/var/lib/galaxy/venv/bin}

function run_web() {
    exec tini -- "${VENV_BIN}/gunicorn" \
        -w 2 -b 0.0.0.0:8000 \
        galaxy.wsgi:application
}

function run_worker() {
    exec tini -- "${VENV_BIN}/python" manage.py celeryd \
        -B --autoreload -Q 'celery,import_tasks,login_tasks'
}

function run_service() {
    case $1 in
        web)
            run_web
        ;;
        worker)
            run_worker
        ;;
    esac
}

case "$1" in
    run)
        run_service "${@:2}"
    ;;
    manage)
        exec "${VENV_BIN}/python" manage.py "${@:2}"
    ;;
esac

exec "$@"
