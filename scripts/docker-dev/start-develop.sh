#!/bin/bash

set -o xtrace
set -o errexit

cd /galaxy

make waitenv

if [ "${TEST}" != "1" ]; then
    make migrate
    make build_indexes
fi 

if [ "${TMUX}" == "1" ] || [ "${TEST}" == "1" ]; then 
    scripts/docker-dev/sleep.sh
else
    ${VENV_BIN}/honcho start -f "scripts/docker-dev/Procfile"
fi
