#!/bin/bash

set -o errexit
set -o nounset

readonly GALAXY_VENV=${GALAXY_VENV}


wait_tcp_port() {
    local -r host="$1"
    local -r port="$2"

    until timeout 1 /bin/bash -c "> /dev/tcp/${host}/${port} 2> /dev/null"; do
        echo "Waiting for TCP port ${host}:${port}..."
        sleep 1
    done
}

wait_forever() {
    while sleep 3600; do :; done
}

activate_venv() {
    echo "Activating virtual environment \"${GALAXY_VENV}\"..."
    # shellcheck disable=SC1090
    VIRTUAL_ENV_DISABLE_PROMPT=1 \
        source "${GALAXY_VENV}/bin/activate"
}

install_galaxy_dev() {
    echo "Installing galaxy in development mode..."
    "${GALAXY_VENV}/bin/pip" install -q -e '/galaxy/'
}

install_node_deps() {
    echo "Installing node dependencies..."
    pushd /galaxy/galaxyui
    yarn install --non-interactive --no-progress
    popd
}

run_migrations() {
    echo "Running migrations..."
    "${GALAXY_VENV}/bin/galaxy-manage" migrate --noinput
}

prepare_env() {
    activate_venv
    install_galaxy_dev
    install_node_deps
    wait_tcp_port postgres 5432
    run_migrations
    wait_tcp_port rabbitmq 5672
    wait_tcp_port redis 6379
    wait_tcp_port influxdb 8086
}

run_api() {
    exec "${GALAXY_VENV}/bin/galaxy-manage" runserver '0.0.0.0:8888'
}

run_ng() {
    cd /galaxy/galaxyui
    exec ng serve --disable-host-check \
        --host 0.0.0.0 --port 8000 \
        --poll 5000 --watch --live-reload \
        --progress=false --proxy-config proxy.conf.js
}

run_celery_beat() {
    exec "${GALAXY_VENV}/bin/galaxy-manage" \
        celery beat \
        --loglevel INFO
}

run_celery_worker() {
    exec "${GALAXY_VENV}/bin/galaxy-manage" \
        celery worker \
        --loglevel INFO
}

run_pulp_content_app() {
    exec "${GALAXY_VENV}/bin/gunicorn" \
          pulpcore.content:server --bind 'localhost:8080' \
          --worker-class 'aiohttp.GunicornWebWorker' -w 2
}

run_pulp_resource_manager() {
    exec "${GALAXY_VENV}/bin/rq" worker \
        -w 'pulpcore.tasking.worker.PulpWorker' \
        -n 'resource_manager@%%h' \
        -c 'pulpcore.rqconfig' \
        --pid='/var/run/galaxy/resource_manager.pid'
}

run_pulp_worker() {
    local -r worker_id="$1"

    exec "${GALAXY_VENV}/bin/rq" worker \
        -w 'pulpcore.tasking.worker.PulpWorker' \
        -n "reserved_resource_worker_${worker_id}@%h" \
        -c 'pulpcore.rqconfig' \
        --pid="/var/run/galaxy/worker_${worker_id}.pid"
}

run() {
    local -r action="$1"

    case "$action" in
        'api')
            run_api
        ;;
        'ng')
            run_ng
        ;;
        'celery-beat')
            run_celery_beat
        ;;
        'celery-worker')
            run_celery_worker
        ;;
        'pulp-content-app')
            run_pulp_content_app
        ;;
        'pulp-resource-manager')
            run_pulp_resource_manager
        ;;
        'pulp-worker')
            shift
            run_pulp_worker "$@"
        ;;
        *)
            echo "Invalid command"
            exit 1
        ;;

    esac
}

start_tmux() {
    echo "Starting tmux..."
    tmux start \; source "scripts/docker/dev/tmux.conf"
    wait_forever
}

start_honcho() {
    exec "${GALAXY_VENV}/bin/honcho" start -f "scripts/docker/dev/Procfile"
}

start() {
    local -r action="$1"
    shift

    prepare_env

    case "$action" in
        'tmux')
            start_tmux
        ;;
        'honcho')
            start_honcho
        ;;
        *)
            echo "Invalid command"
            exit 1
        ;;
    esac
}

manage() {
    "${GALAXY_VENV}/bin/galaxy-manage" "$@"
}

main() {
    local -r action="$1"

    case "$action" in
        'run')
            shift
            run "$@"
        ;;
        'start')
            shift
            start "$@"
        ;;
        'manage')
            shift
            manage "$@"
        ;;
        *)
            exec "$@"
        ;;
    esac
}

main "$@"
