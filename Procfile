# For development only
# Run from inside the django container with `honcho start`
runserver:   /venv/bin/galaxy-manage runserver 0.0.0.0:8000 
celeryd:     /venv/bin/galaxy-manage celeryd -B --autoreload -Q celery,import_tasks,login_tasks 
