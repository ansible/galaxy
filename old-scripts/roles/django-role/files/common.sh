PYTHON="/venv/bin/python"
PG_ISREADY="/usr/pgsql-9.5/bin/pg_isready"

function waitenv() {
     ${PYTHON} manage.py waitenv
}

function run_migrations() {
     ${PYTHON} manage.py migrate --noinput --fake-initial
}

function update_django_site() {
    psql -h postgres -d galaxy -U galaxy -f /setup/update_site.sql
}

function init_django_db() {
    echo "Waiting for Environment..."
    waitenv

    echo "Running migrations..."
    run_migrations

    echo "Updating django site..."
    update_django_site

    touch /setup/dbinit.completed
    # TODO: Rebuild index?
}
