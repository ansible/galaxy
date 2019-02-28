#!/bin/bash

set -o nounset
set -o errexit

readonly VENV_BIN=${VENV_BIN:-/var/lib/galaxy/venv/bin}
readonly GALAXY_NUM_WORKERS=${GALAXY_NUM_WORKERS:-1}

# shellcheck disable=SC2034
VIRTUAL_ENV_DISABLE_PROMPT=1
source "${VENV_BIN}/activate"

# FIXME(cutwater): Yet another workaround for running entrypoint not as PID 1
# All run commands should be implemented outside entrypoint (e.g. in manage.py)
function _exec_cmd() {
    [ $$ -eq 1 ] && set -- tini -- "$@"
    exec "$@"
}

function run_web() {
    _exec_cmd "${VENV_BIN}/gunicorn" \
        --bind 0.0.0.0:8000 \
        --workers "${GALAXY_NUM_WORKERS}" \
        --access-logfile '-' \
        --error-logfile '-' \
        galaxy.wsgi:application
}

function run_worker() {
    _exec_cmd "${VENV_BIN}/galaxy-manage" celeryd \
        --beat \
        --concurrency "${GALAXY_NUM_WORKERS}" \
        --loglevel WARNING \
        --queues 'celery,import_tasks,login_tasks,admin_tasks,user_tasks,star_tasks'
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
        _exec_cmd "${VENV_BIN}/galaxy-manage" "${@:2}"
    ;;
esac

_exec_cmd "$@"
