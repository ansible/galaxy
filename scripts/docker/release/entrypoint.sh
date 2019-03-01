#!/bin/bash

set -o nounset
set -o errexit

readonly GALAXY_VENV=${GALAXY_VENV:-/usr/share/galaxy/venv}
readonly GALAXY_NUM_WORKERS=${GALAXY_NUM_WORKERS:-1}

# shellcheck disable=SC2034
VIRTUAL_ENV_DISABLE_PROMPT=1
# shellcheck disable=SC1090
source "${GALAXY_VENV}/bin/activate"

# FIXME(cutwater): Yet another workaround for running entrypoint not as PID 1
# All run commands should be implemented outside entrypoint (e.g. in manage.py)
_exec_cmd() {
    [[ $$ -eq 1 ]] && set -- tini -- "$@"
    exec "$@"
}

run_api() {
    _exec_cmd "${GALAXY_VENV}/bin/gunicorn" \
        --bind 0.0.0.0:8000 \
        --workers "${GALAXY_NUM_WORKERS}" \
        --access-logfile '-' \
        --error-logfile '-' \
        galaxy.wsgi:application
}

run_celery_worker() {
    _exec_cmd "${GALAXY_VENV}/bin/galaxy-manage" celery worker \
        --concurrency "${GALAXY_NUM_WORKERS}" \
        --loglevel WARNING \
        --queues 'celery,import_tasks,login_tasks,admin_tasks,user_tasks,star_tasks'
}

run_celery_beat() {
    _exec_cmd "${GALAXY_VENV}/bin/galaxy-manage" celery beat \
        --loglevel WARNING
}

run_pulp_content_app() {
    _exec_cmd "${GALAXY_VENV}/bin/gunicorn" \
          pulpcore.content:server \
          --bind '0.0.0.0:8080' \
          --worker-class 'aiohttp.GunicornWebWorker' \
          --workers "${GALAXY_NUM_WORKERS}"
}

run_pulp_resource_manager() {
    _exec_cmd "${GALAXY_VENV}/bin/rq" worker \
        -w 'pulpcore.tasking.worker.PulpWorker' \
        -n 'resource_manager@%%h' \
        -c 'pulpcore.rqconfig' \
        --pid='/var/run/galaxy/resource_manager.pid'
}

run_pulp_worker() {
    _exec_cmd "${GALAXY_VENV}/bin/rq" worker \
        -w 'pulpcore.tasking.worker.PulpWorker' \
        -n "reserved_resource_worker@%h" \
        -c 'pulpcore.rqconfig' \
        --pid="/var/run/galaxy/worker.pid"
}

run_service() {
    case $1 in
        'api')
            run_api
        ;;
        'celery-worker')
            run_celery_worker
        ;;
        'celery-beat')
            run_celery_beat
        ;;
        'pulp-content-app')
            run_pulp_content_app
        ;;
        'pulp-resource-manager')
            run_pulp_resource_manager
        ;;
        'pulp-worker')
            run_pulp_worker
        ;;
        *)
            echo "Invalid command"
            exit 1
        ;;
    esac
}

main() {
    case "$1" in
        'run')
            run_service "${@:2}"
        ;;
        'manage')
            _exec_cmd "${GALAXY_VENV}/bin/galaxy-manage" "${@:2}"
        ;;
        *)
            _exec_cmd "$@"
        ;;
    esac
}

main "$@"
