#!/bin/bash

set -o xtrace
set -o errexit

cd /galaxy

make waitenv
make collectstatic
make build/static

if [ -d /galaxy/build/static/admin ]; then
    cp -R /galaxy/build/static/admin /galaxy/galaxy/static/
fi

cd /galaxy/galaxyui
yarn install
cd /galaxy

if [ "${TEST}" != "1" ]; then
    make migrate
fi

if [ "${TMUX}" == "1" ] || [ "${TEST}" == "1" ]; then 
    scripts/docker-dev/sleep.sh
else
    ${VENV_BIN}/honcho start -f "scripts/docker-dev/Procfile"
fi
