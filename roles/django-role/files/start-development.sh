#!/bin/bash
set +x

# remove any lingering log files that might be owned by root
rm -f /galaxy_logs/*.log 

if [ ! -f /setup/dbinit.completed ]; then
     cd /setup
     /venv/bin/ansible-playbook -i inventory dbinit.yml
     cd - 
else
     /venv/bin/galaxy-manage makemigrations
     /venv/bin/galaxy-manage migrate --noinput
fi

/venv/bin/honcho start
