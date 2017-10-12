PYTHON="/venv/bin/python"
PG_ISREADY="/usr/pgsql-9.5/bin/pg_isready"

function wait_for_postgres() {
    local timeout=10
    local pg_isready="${PG_ISREADY} -h postgres -p 5432"
    until ${pg_isready} &>/dev/null || [ ${timeout} -le 0 ]; do
        sleep 1
        (( timeout-- ))
    done
}

function run_migrations() {
     ${PYTHON} manage.py migrate --noinput --fake-initial
}

function update_django_site() {
    psql -h postgres -d galaxy -U galaxy -f /setup/update_site.sql
}

function init_django_db() {
    echo "Waiting for PostgreSQL..."
    wait_for_postgres

    echo "Running migrations..."
    run_migrations

    echo "Updating django site..."
    update_django_site

    touch /setup/dbinit.completed
    # TODO: Rebuild index?
}
