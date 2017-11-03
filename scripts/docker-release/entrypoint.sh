#!/bin/bash

set -o nounset
set -o errexit

readonly VENV_BIN=${VENV_BIN:-/var/lib/galaxy/venv/bin}

# FIXME(cutwater): Yet another workaround for running entrypoint not as PID 1
# All run commands should be implemented outside entrypoint (e.g. in manage.py)
function _exec_cmd() {
    [ $$ -eq 1 ] && set -- tini -- "$@"
    exec "$@"
}

function run_web() {
    _exec_cmd "${VENV_BIN}/gunicorn" \
        -w 2 -b 0.0.0.0:8000 \
        --worker-class gevent \
        galaxy.wsgi:application
}

function run_worker() {
    _exec_cmd "${VENV_BIN}/python" manage.py celeryd \
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
        _exec_cmd "${VENV_BIN}/python" manage.py "${@:2}"
    ;;
esac

_exec_cmd "$@"
