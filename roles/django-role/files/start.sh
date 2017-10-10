#!/bin/bash

if [ ! -f /setup/dbinit.completed ]; then
     cd /setup
     /venv/bin/ansible-playbook -i inventory dbinit.yml
     if [ "$?" != "0" ]; then
         exit 1
     fi
     cd -
fi

exec /venv/bin/gunicorn -w 2 -b 0.0.0.0:8000 galaxy.wsgi:application
