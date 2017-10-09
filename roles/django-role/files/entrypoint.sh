#!/bin/bash

set -x

if [ ! -f /setup/dbinit.completed ]; then
     cd /setup
     ansible-playbook -i inventory dbinit.yml
     cd /
fi

exec "$@"
