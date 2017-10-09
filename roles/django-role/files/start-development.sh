#!/bin/bash
set +x

# remove any lingering log files that might be owned by root
rm -f /galaxy_logs/*.log

if [ -f /setup/dbinit.completed ]; then
     /venv/bin/python ./manage.py makemigrations
     if [ "$?" != "0" ]; then
         exit 1
     fi
     /venv/bin/python ./manage.py migrate --noinput
     if [ "$?" != "0" ]; then
         exit 1
     fi
fi

exec /venv/bin/python /galaxy/manage.py runserver 0.0.0.0:8000 --nostatic
