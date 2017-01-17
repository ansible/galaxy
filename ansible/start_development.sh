#!/bin/bash
set +x

# remove any lingering log files that might be owned by root
rm -f /galaxy_logs/*.log 

if [ ! -f /setup/dbinit.completed ]; then
     cd /setup
     ansible-playbook -i inventory dbinit.yml
     cd - 
else
     galaxy-manage makemigrations
     galaxy-manage migrate --noinput
fi

honcho start
