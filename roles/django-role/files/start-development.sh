#!/bin/bash
set +x

# remove any lingering log files that might be owned by root
rm -f /galaxy_logs/*.log 

if [ ! -f /setup/dbinit.completed ]; then
     cd /setup
     /venv/bin/ansible-playbook -i inventory dbinit.yml
     if [ "$?" != "0" ]; then 
         exit 1
     fi
     cd - 
else
     /venv/bin/galaxy-manage makemigrations
     if [ "$?" != "0" ]; then 
         exit 1
     fi
     /venv/bin/galaxy-manage migrate --noinput
     if [ "$?" != "0" ]; then 
         exit 1
     fi
fi

/venv/bin/honcho start
