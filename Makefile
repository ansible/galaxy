PYTHON=python

VENV_BIN=/var/lib/galaxy/venv/bin

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

DOCKER_COMPOSE=docker-compose -f ./scripts/compose-dev.yml -p galaxy


.PHONY: help
help:
	@echo "Prints help"

# ---------------------------------------------------------
# Common targets
# ---------------------------------------------------------

.PHONY: runserver
runserver:
	python manage.py runserver 0.0.0.0:8888

.PHONY: celery
celery:
	python manage.py celeryd -B --autoreload -Q 'celery,import_tasks,login_tasks'

.PHONY: gulp
gulp:
	/usr/local/bin/gulp

.PHONY: waitenv
waitenv:
	@echo "Waiting for services to start..."
	python ./manage.py waitenv

.PHONY: migrate
migrate:
	@echo "Run migrations"
	python ./manage.py migrate --noinput

.PHONY: build_indexes
build_indexes:
	@echo "Rebuild Custom Indexes"
	python ./manage.py rebuild_galaxy_indexes
	@echo "Rebuild Search Index"
	python ./manage.py rebuild_index --noinput

.PHONY: clean_dist
clean_dist:
	rm -rf dist/*
	rm -rf build rpm-build *.egg-info
	rm -rf debian deb-build
	rm -f galaxy/static/dist/*.js
	find . -type f -regex ".*\.py[co]$$" -delete

# ---------------------------------------------------------
# Build targets
# ---------------------------------------------------------

.PHONY: sdist
sdist: clean_dist ui_build
	if [ "$(OFFICIAL)" = "yes" ] ; then \
	   $(PYTHON) setup.py release_build; \
	else \
	   BUILD=$(BUILD) $(PYTHON) setup.py sdist_galaxy; \
	fi

# ---------------------------------------------------------
# Test targets
# ---------------------------------------------------------

.PHONY: test/flake8
test/flake8:
	flake8 --config=tox.ini galaxy

# ---------------------------------------------------------
# Docker targets
# ---------------------------------------------------------

.PHONY: docker/test-flake8
docker/test-flake8:
	docker run --rm -i -t -v $(CURDIR):/galaxy galaxy-dev:latest make test/flake8

# ---------------------------------------------------------
# Development targets
# ---------------------------------------------------------

.PHONY: dev/build
dev/build:
	scripts/build-docker-dev.sh

.PHONY: dev/createsuperuser
dev/createsuperuser:
	@echo "Create Superuser"
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/python ./manage.py createsuperuser

.PHONY: dev/migrate
dev/migrate:
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/python ./manage.py migrate --noinput

.PHONY: dev/makemigrations
dev/makemigrations:
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/python ./manage.py makemigrations main

.PHONY: dev/flake8
dev/flake8:
	@echo "Running flake8"
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/flake8 --config=tox.ini galaxy

.PHONY: dev/test
dev/test:
	@echo "Running tests"
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/python ./manage.py test

.PHONY: dev/waitenv
dev/waitenv:
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/python ./manage.py waitenv

.PHONY: dev/up
dev/up:
	$(DOCKER_COMPOSE) up

# Start all containers detached
.PHONY: dev/up_detached
dev/up_detached:
	$(DOCKER_COMPOSE) up -d

.PHONY: dev/up_tmux
dev/up_tmux:
	# Run before dev/tmux to start containers detached and no processes running in the galaxy container.
	@TMUX=1 $(DOCKER_COMPOSE) up -d

.PHONY: dev/down
dev/down:
	$(DOCKER_COMPOSE) down

.PHONY: dev/restart
dev/restart:
	# Restart one or more services
	$(DOCKER_COMPOSE) restart $(filter-out $@,$(MAKECMDGOALS))

.PHONY: dev/stop
dev/stop:
	# Stop one or more services
	$(DOCKER_COMPOSE) stop $(filter-out $@,$(MAKECMDGOALS))

# Create the tmux session. Do NOT call directly. Use dev/tmux or dev/tmuxcc instead.
.PHONY: dev/tmux_noattach
dev/tmux_noattach:
	tmux new-session -d -s galaxy -n galaxy \; \
		 set-option -g allow-rename off \; \
		 send-keys "make runserver" Enter \; \
		 new-window -n celery \; \
		 send-keys "make celery" Enter \; \
		 new-window -n gulp \; \
		 send-keys "make gulp" Enter

.PHONY: dev/tmux
dev/tmux:
	# Connect to the galaxy container, start processes, and pipe stdout/stderr through a tmux session
	$(DOCKER_COMPOSE) exec galaxy bash -c 'make dev/tmux_noattach; tmux -2 attach-session -t galaxy'

.PHONY: dev/tmuxcc
dev/tmuxcc: dev/tmux_noattach
	# Same as above using iTerm's built-in tmux support
	$(DOCKER_COMPOSE) exec galaxy bash -c 'make dev/tmux_noattach; tmux -2 -CC attach-session -t galaxy'

.PHONY: dev/gulp_build
dev/gulp_build:
	# build UI components
	$(DOCKER_COMPOSE) exec galaxy bash -c '/usr/local/bin/gulp build'

.PHONY: dev/export-test-data
export-test-data:
	@echo Export data to test-data/role_data.dmp.gz
	$(DOCKER_COMPOSE) /galaxy/test-data/export.sh

.PHONY: dev/import-test-data
import_test_data:
	@echo Import data from test-data/role_data.dmp.gz
	$(DOCKER_COMPOSE) /galaxy/test-data/import.sh

.PHONY: dev/refresh-role-counts
refresh-role-counts:
	@echo Refresh role counts
	$(DOCKER_COMPOSE) $(VENV_BIN)/python ./manage.py refresh_role_counts

%:
	@:
