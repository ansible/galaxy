#!/bin/bash

# shellcheck disable=SC2034
VIRTUAL_ENV_DISABLE_PROMPT=1
# shellcheck disable=SC1090
source "${VENV_BIN}/activate"

exec "$@"
