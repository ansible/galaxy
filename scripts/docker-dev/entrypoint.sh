#!/bin/bash

VIRTUAL_ENV_DISABLE_PROMPT=1
source "${VENV_BIN}/activate"

exec "$@"
