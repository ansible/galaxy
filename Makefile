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

.PHONY: clean clean_dist refresh migrate migrate_empty makemigrations build_from_scratch build \
        run sdist stop requirements ui_build

# Remove containers, images and ~/.galaxy
clean:
	@./ansible/clean.sh

# Refresh development environment after pulling new code.
refresh: clean build run 

# Create and execute database migrations
migrate:
	@docker exec -i -t ansible_django_1 galaxy-manage makemigrations main --noinput
	@docker exec -i -t ansible_django_1 galaxy-manage migrate --noinput

# Create an empty migration
migrate_empty:
	@docker exec -i -t ansible_django_1 galaxy-manage makemigrations --empty main

makemigrations:
	@docker exec -i -t ansible_django_1 galaxy-manage makemigrations main

psql:
	@docker exec -i -t ansible_django_1 psql -h postgres -d galaxy -U galaxy

# Build Galaxy images 
build_from_scratch:
	ansible-container --var-file ansible/develop.yml --from-scratch -- -e"@/ansible-container/ansible/develop.yml"

build:
	ansible-container --var-file ansible/develop.yml build -- -e"@/ansible-container/ansible/develop.yml"

build_indexes:
	@echo "Rebuild Search Index"
	@docker exec -i -t ansible_django_1 galaxy-manage rebuild_index --noinput
	@echo "Rebuild Custom Indexes"
	@docker exec -i -t ansible_django_1 galaxy-manage rebuild_galaxy_indexes

# Start Galaxy containers
run:
	ansible-container --var-file ansible/develop.yml run -d memcache; \
	ansible-container --var-file ansible/develop.yml run -d rabbit; \
	ansible-container --var-file ansible/develop.yml run -d postgres; \
	ansible-container --var-file ansible/develop.yml run -d elastic; \
	ansible-container --var-file ansible/develop.yml --debug run django gulp

stop:
	@ansible-container stop --force

sdist: clean ui_build
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
