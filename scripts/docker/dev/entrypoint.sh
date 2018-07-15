#!/bin/bash

# shellcheck disable=SC2034
VIRTUAL_ENV_DISABLE_PROMPT=1
source "${VENV_BIN}/activate"

exec "$@"
