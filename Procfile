# For development only
# Run from inside the django container with `honcho start`
runserver:   /venv/bin/python /galaxy/manage.py runserver 0.0.0.0:8000 --nostatic
celeryd:     /venv/bin/python /galaxy/manage.py celeryd -B --autoreload -Q celery,import_tasks,login_tasks 
