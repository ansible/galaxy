#!/bin/bash

set -o xtrace
set -o errexit

cd /galaxy

make waitenv
make migrate
make build_indexes

if [ "${TMUX}" == "1" ]; then 
    scripts/docker-dev/sleep.sh
else
    ${VENV_DIR}/bin/honcho start -f "scripts/docker-dev/Procfile"
fi
