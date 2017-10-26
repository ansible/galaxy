PYTHON=python
SITELIB=$(shell $(PYTHON) -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")

DATE := $(shell date -u +%Y%m%d%H%M)

VERSION=$(shell $(PYTHON) -c "from galaxy import __version__; print(__version__.split('-')[0])")
RELEASE=$(shell $(PYTHON) -c "from galaxy import __version__; print(__version__.split('-')[1])")

#ansible-container options
ifeq ($(DETACHED),yes)
  detach_option="-d"
else
  detach_option=""
endif

ifneq ($(OFFICIAL),yes)
BUILD=dev$(DATE)
SDIST_TAR_FILE=galaxy-$(VERSION)-$(BUILD).tar.gz
SETUP_TAR_NAME=galaxy-setup-$(VERSION)-$(BUILD)
else
BUILD=
SDIST_TAR_FILE=galaxy-$(VERSION).tar.gz
SETUP_TAR_NAME=galaxy-setup-$(VERSION)
RPM_PKG_RELEASE=$(RELEASE)
DEB_BUILD_DIR=deb-build/galaxy-$(VERSION)
DEB_PKG_RELEASE=$(VERSION)-$(RELEASE)
endif

VENV_BIN=/var/lib/galaxy/venv/bin

.PHONY: clean_dist \
        sdist requirements ui_build export_test_data import_test_data \
        refresh_role_counts

.PHONY: dev/build
dev/build:
	scripts/build-docker-dev.sh

.PHONY: dev/createsuperuser
dev/createsuperuser:
	@echo "Create Superuser"
	@docker-compose -f ./scripts/compose-dev.yml -p galaxy exec galaxy bash -c '${VENV_BIN}/python ./manage.py createsuperuser'

.PHONY: dev/migrate
dev/migrate:
	docker-compose -f ./scripts/compose-dev.yml -p galaxy exec galaxy bash -c '${VENV_BIN}/python ./manage.py migrate --noinput'

.PHONY: dev/makemigrations
dev/makemigrations:
	docker-compose -f ./scripts/compose-dev.yml -p galaxy exec galaxy bash -c '${VENV_BIN}/python ./manage.py makemigrations main'

.PHONY: dev/flake8
dev/flake8:
	@echo "Running flake8"
	@docker-compose -f ./scripts/compose-dev.yml -p galaxy exec galaxy bash -c '${VENV_BIN}/flake8 --config=tox.ini galaxy'

.PHONY: dev/test
dev/test:
	@echo "Running tests"
	@docker-compose -f ./scripts/compose-dev.yml -p galaxy exec galaxy bash -c '${VENV_BIN}/python ./manage.py test'

.PHONY: dev/up
dev/up:
	docker-compose -f ./scripts/compose-dev.yml -p galaxy up

.PHONY: dev/up_detached
dev/up_detached:
	# Start all containers detached
	docker-compose -f ./scripts/compose-dev.yml -p galaxy up -d

.PHONY: dev/up_tmux
dev/up_tmux:
	# Run before dev/tmux to start containers detached and no processes running in the galaxy container.
	TMUX=1 docker-compose -f ./scripts/compose-dev.yml -p galaxy up -d

.PHONY: dev/down
dev/down:
	docker-compose -f ./scripts/compose-dev.yml -p galaxy down

.PHONY: dev/restart
dev/restart:
	# Restart one or more services
	docker-compose -f ./scripts/compose-dev.yml -p galaxy restart $(filter-out $@,$(MAKECMDGOALS)) 

.PHONY: dev/stop
dev/stop:
	# Stop one or more services
	docker-compose -f ./scripts/compose-dev.yml -p galaxy stop $(filter-out $@,$(MAKECMDGOALS)) 

.PHONY: dev/tmux_noattach
dev/tmux_noattach:
	# Create the tmux session. Do NOT call directly. Use dev/tmux or dev/tmuxcc instead.
	tmux new-session -d -s galaxy -n galaxy 'bash -c "make runserver; exec bash"' 
	tmux new-window -t galaxy:1 -n celery 'bash -c "make celery; exec bash"'
	tmux new-window -t galaxy:2 -n gulp 'bash -c "make gulp; exec bash"'
	tmux select-window -t galaxy:0

.PHONY: dev/tmux
dev/tmux: 
	# Connect to the galaxy container, start processes, and pipe stdout/stderr through a tmux session
	docker-compose -f ./scripts/compose-dev.yml -p galaxy exec galaxy bash -c 'make dev/tmux_noattach; tmux -2 attach-session -t galaxy'

.PHONY: dev/tmuxcc
dev/tmuxcc: dev/tmux_noattach
	# Same as above using iTerm's built-in tmux support
	docker-compose -f ./scripts/compose-dev.yml -p galaxy exec galaxy bash -c 'make dev/tmux_noattach; tmux -2 -CC attach-session -t galaxy'

.PHONY: dev/gulp_build
dev/gulp_build:
	# build UI components
	docker-compose -f ./scripts/compose-dev.yml -p galaxy exec galaxy bash -c '/usr/local/bin/gulp build'

sdist: clean_dist ui_build
	if [ "$(OFFICIAL)" = "yes" ] ; then \
	   $(PYTHON) setup.py release_build; \
	else \
	   BUILD=$(BUILD) $(PYTHON) setup.py sdist_galaxy; \
	fi

clean_dist:
	rm -rf dist/*
	rm -rf build rpm-build *.egg-info
	rm -rf debian deb-build
	rm -f galaxy/static/dist/*.js
	find . -type f -regex ".*\.py[co]$$" -delete

export_test_data:
	@echo Export data to test-data/role_data.dmp.gz
	@docker exec -i -t galaxy_django_1 /galaxy/test-data/export.sh

import_test_data:
	@echo Import data from test-data/role_data.dmp.gz
	@docker exec -i -t galaxy_django_1 /galaxy/test-data/import.sh

refresh_role_counts:
	@echo Refresh role counts
	@docker exec -i -t galaxy_django_1 /venv/bin/python ./manage.py refresh_role_counts

.PHONY: celery
celery:
	${VENV_DIR}/bin/python manage.py celeryd -B --autoreload -Q 'celery,import_tasks,login_tasks'

.PHONY: runserver
runserver:
	${VENV_DIR}/bin/python manage.py runserver 0.0.0.0:8888

.PHONY: gulp
gulp:
	/usr/local/bin/gulp

.PHONY: waitenv
waitenv:
	@echo "Waiting for services to start..."
	${VENV_DIR}/bin/python ./manage.py waitenv

.PHONY: migrate
migrate:
	@echo "Run migrations"
	${VENV_DIR}/bin/python ./manage.py migrate --noinput

.PHONY: build_indexes
build_indexes:
	@echo "Rebuild Custom Indexes"
	${VENV_DIR}/bin/python ./manage.py rebuild_galaxy_indexes
	@echo "Rebuild Search Index"
	${VENV_DIR}/bin/python ./manage.py rebuild_index --noinput

%:      
	@:
