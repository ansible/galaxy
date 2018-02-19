#!/bin/bash

set -o nounset
set -o errexit

VIRTUAL_ENV_DISABLE_PROMPT=1
VENV_BIN=${VENV_BIN:-/var/lib/galaxy/venv}
source ${VENV_BIN}/activate

make ng_build
mkdir -p build/static
make build/dist
make collectstatic
