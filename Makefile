PYTHON=python
SITELIB=$(shell $(PYTHON) -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")

# Get the branch information from git
GIT_DATE := $(shell git log -n 1 --format="%ai")
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

.PHONY: clean clean_dist clean_images clean_containers \
        refresh migrate migrate_empty makemigrations build_from_scratch \
        build build_debug \
        run run_production\
        flake8 \
        build_indexes \
        sdist stop requirements ui_build export_test_data import_test_data createsuperuser \
        refresh_role_counts shell

# Remove containers, images and ~/.galaxy
clean:
	@./ansible/clean.sh

# Refresh development environment after pulling new code.
refresh: clean build run 

# Remove containers
clean_containers:
	ansible/clean.sh containers

# Remove images
clean_images:
	ansible/clean.sh images

# Create and execute database migrations
migrate:
	@docker exec -i -t ansible_django_1 /venv/bin/galaxy-manage makemigrations main --noinput
	@docker exec -i -t ansible_django_1 /venv/bin/galaxy-manage migrate --noinput

# Create an empty migration
migrate_empty:
	@docker exec -i -t ansible_django_1 /venv/bin/galaxy-manage makemigrations --empty main

makemigrations:
	@docker exec -i -t ansible_django_1 /venv/bin/galaxy-manage makemigrations main

psql:
	@docker exec -i -t ansible_django_1 psql -h postgres -d galaxy -U galaxy

# Build Galaxy images 
build_from_scratch:
	ansible-container --var-file ansible/develop.yml build --from-scratch -- -e"@/ansible-container/ansible/develop.yml"

build:
	ansible-container --var-file ansible/develop.yml build -- -e"@/ansible-container/ansible/develop.yml"

build_debug:
	ansible-container --var-file ansible/develop.yml --debug build -- -e"@/ansible-container/ansible/develop.yml"

build_indexes:
	@echo "Rebuild Custom Indexes"
	@docker exec -i -t ansible_django_1 /venv/bin/galaxy-manage rebuild_galaxy_indexes
	@echo "Rebuild Search Index"
	@docker exec -i -t ansible_django_1 /venv/bin/galaxy-manage rebuild_index --noinput

createsuperuser: 
	@echo "Create Superuser"
	@docker exec -i -t ansible_django_1 /venv/bin/galaxy-manage createsuperuser

# Run flake8 inside the django container
flake8:
	docker run -v ${PWD}:/galaxy -w /galaxy galaxy-django:latest /venv/bin/flake8 --config=tox.ini galaxy

# Start Galaxy containers with django and gulp in the foreground
run:
	ansible-container --var-file ansible/develop.yml run -d memcache rabbit postgres elastic; \
	ansible-container --var-file ansible/develop.yml --debug run django gulp

# Start production
run_production:
	ansible-container --var-file ansible/develop.yml --debug run -d --production

stop:
	@ansible-container stop --force

sdist: clean_dist ui_build
	if [ "$(OFFICIAL)" = "yes" ] ; then \
	   $(PYTHON) setup.py release_build; \
	else \
	   BUILD=$(BUILD) $(PYTHON) setup.py sdist_galaxy; \
	fi

requirements:
	@if [ "$(VIRTUAL_ENV)" ]; then \
	    pip install distribute==0.7.3; \
	    pip install -r requirements.txt; \
	    $(PYTHON) fix_virtualenv_setuptools.py; \
	else \
	    sudo pip install -r requirements.txt; \
	fi

clean_dist:
	rm -rf dist/*
	rm -rf build rpm-build *.egg-info
	rm -rf debian deb-build
	rm -f galaxy/static/dist/*.js
	find . -type f -regex ".*\.py[co]$$" -delete

ui_build:
	node node_modules/gulp/bin/gulp.js build

export_test_data:
	@echo Export data to test-data/role_data.dmp.gz
	@docker exec -i -t ansible_django_1 /galaxy/test-data/export.sh

import_test_data:
	@echo Import data from test-data/role_data.dmp.gz
	@docker exec -i -t ansible_django_1 /galaxy/test-data/import.sh

refresh_role_counts:
	@echo Refresh role counts
	@docker exec -i -t ansible_django_1 /venv/bin/galaxy-manage refresh_role_counts
shell:
	@echo Starting shell on ansible_django_1
	@docker exec -i -t ansible_django_1 /bin/bash

