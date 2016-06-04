PYTHON=python
SITELIB=$(shell $(PYTHON) -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")

# Get the branch information from git
GIT_DATE := $(shell git log -n 1 --format="%ai")
DATE := $(shell date -u +%Y%m%d%H%M)

VERSION=$(shell $(PYTHON) -c "from galaxy import __version__; print(__version__.split('-')[0])")
RELEASE=$(shell $(PYTHON) -c "from galaxy import __version__; print(__version__.split('-')[1])")
ifneq ($(OFFICIAL),yes)
BUILD=dev$(DATE)
SDIST_TAR_FILE=galaxy-$(VERSION)-$(BUILD).tar.gz
SETUP_TAR_NAME=galaxy-setup-$(VERSION)-$(BUILD)
RPM_PKG_RELEASE=$(BUILD)
DEB_BUILD_DIR=deb-build/galaxy-$(VERSION)-$(BUILD)
DEB_PKG_RELEASE=$(VERSION)-$(BUILD)
else
BUILD=
SDIST_TAR_FILE=galaxy-$(VERSION).tar.gz
SETUP_TAR_NAME=galaxy-setup-$(VERSION)
RPM_PKG_RELEASE=$(RELEASE)
DEB_BUILD_DIR=deb-build/galaxy-$(VERSION)
DEB_PKG_RELEASE=$(VERSION)-$(RELEASE)
endif

.PHONY: clean rebase push requirements requirements_pypi develop refresh \
	adduser syncdb migrate dbchange dbshell runserver celeryd test \
	test_coverage coverage_html test_ui test_jenkins dev_build \
	release_build release_clean sdist rpm ui_build

# Remove temporary build files, compiled Python files.
clean:
	rm -rf dist/*
	rm -rf build rpm-build *.egg-info
	rm -rf debian deb-build
	rm -f galaxy/static/dist/*.js
	find . -type f -regex ".*\.py[co]$$" -delete

# Fetch from origin, rebase local commits on top of origin commits.
rebase:
	git pull --rebase origin master

# Push changes to origin.
push:
	git push origin master

# Install third-party requirements needed for development environment 
requirements:
	@if [ "$(VIRTUAL_ENV)" ]; then \
	    pip install distribute==0.7.3; \
	    pip install -r requirements.txt; \
	    $(PYTHON) fix_virtualenv_setuptools.py; \
        else \
	    sudo pip install -r requirements.txt; \
        fi

# Install third-party requirements needed for development environment
# (downloading from PyPI if necessary).
requirements_pypi:
	@if [ "$(VIRTUAL_ENV)" ]; then \
	    pip install -r requirements.txt; \
	    $(PYTHON) fix_virtualenv_setuptools.py; \
	else \
	    sudo pip install -r requirements.txt; \
	fi

# "Install" galaxy package in development mode.  Creates link to working
# copy in site-packages and installs galaxy-manage command.
develop:
	@if [ "$(VIRTUAL_ENV)" ]; then \
	    $(PYTHON) setup.py develop; \
	else \
	    sudo $(PYTHON) setup.py develop; \
	fi

# Refresh development environment after pulling new code.
refresh: clean requirements develop migrate

Vagrantfile:
	cp provisioning/development/$@ $@

start_vm: Vagrantfile
	vagrant up

# Create Django superuser.
adduser:
	$(PYTHON) manage.py createsuperuser

# Create initial database tables (excluding migrations).
syncdb:
	$(PYTHON) manage.py makemigration --noinput
	$(PYTHON) manage.py migrate --noinput

# Create database tables and apply any new migrations.
migrate: syncdb
	$(PYTHON) manage.py migrate --noinput

# Run after making changes to the models to create a new migration.
dbchange:
	$(PYTHON) manage.py schemamigration main v14_changes --auto

# access database shell, asks for password
dbshell:
	sudo -u postgres psql -d galaxy

server_noattach:
	tmux new-session -d -s galaxy 'exec make runserver'
	tmux rename-window 'Galaxy'
	tmux select-window -t galaxy:0
	tmux split-window -v 'exec make celeryd'

server: server_noattach
	tmux -2 attach-session -t galaxy

servercc: server_noattach
	tmux -2 -CC attach-session -t galaxy

# Run the built-in development webserver (by default on http://localhost:8013).
runserver:
	$(PYTHON) manage.py runserver 0.0.0.0:8000

# Run to start the background celery worker for development. Listens to all queues.
celeryd:
	$(PYTHON) manage.py celeryd -l DEBUG -B --autoreload -Q celery,import_tasks,login_tasks

# Run all API unit tests.
test:
	$(PYTHON) manage.py test -v2 main

# Run all API unit tests with coverage enabled.
test_coverage:
	coverage run manage.py test -v2 main

# Output test coverage as HTML (into htmlcov directory).
coverage_html:
	coverage html

# Run UI unit tests using Selenium.
test_ui:
	$(PYTHON) manage.py test -v2 ui

# Run API unit tests across multiple Python/Django versions with Tox.
test_tox:
	tox -v

# Run unit tests to produce output for Jenkins.
test_jenkins:
	$(PYTHON) manage.py jenkins -v2

# Build minified JS/CSS.
ui_build:
	node node_modules/gulp/bin/gulp.js build	

# Build a pip-installable package into dist/ with a timestamped version number.
dev_build: 
	$(PYTHON) setup.py dev_build

# Build a pip-installable package into dist/ with the release version number.
release_build:
	$(PYTHON) setup.py release_build

# Build AWX setup tarball.
setup_tarball:
	@cp -a setup $(SETUP_TAR_NAME)
	@tar czf $(SETUP_TAR_NAME).tar.gz $(SETUP_TAR_NAME)/
	@rm -rf $(SETUP_TAR_NAME)

release_clean:
	-(rm *.tar)
	-(rm -rf ($RELEASE))

sdist: clean ui_build
	if [ "$(OFFICIAL)" = "yes" ] ; then \
	   $(PYTHON) setup.py release_build; \
	else \
	   BUILD=$(BUILD) $(PYTHON) setup.py sdist_galaxy; \
	fi

rpmtar: sdist
	if [ "$(OFFICIAL)" != "yes" ] ; then \
	   (cd dist/ && tar zxf $(SDIST_TAR_FILE)) ; \
	   (cd dist/ && mv galaxy-$(VERSION)-$(BUILD) galaxy-$(VERSION)) ; \
	   (cd dist/ && tar czf galaxy-$(VERSION).tar.gz galaxy-$(VERSION)) ; \
	fi

rpm: rpmtar
	@mkdir -p rpm-build
	@cp dist/galaxy-$(VERSION).tar.gz rpm-build/
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir %{_topdir}" \
	--define '_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm' \
	--define "_sourcedir  %{_topdir}" \
	--define "_pkgrelease  $(RPM_PKG_RELEASE)" \
	-ba packaging/rpm/galaxy.spec

deb: sdist
	@mkdir -p deb-build
	@cp dist/$(SDIST_TAR_FILE) deb-build/
	(cd deb-build && tar zxf $(SDIST_TAR_FILE))
	(cd $(DEB_BUILD_DIR) && dh_make --indep --yes -f ../$(SDIST_TAR_FILE) -p galaxy-$(VERSION))
	@rm -rf $(DEB_BUILD_DIR)/debian
	@cp -a packaging/debian $(DEB_BUILD_DIR)/
	@echo "galaxy_$(DEB_PKG_RELEASE).deb admin optional" > $(DEB_BUILD_DIR)/debian/realfiles
	(cd $(DEB_BUILD_DIR) && PKG_RELEASE=$(DEB_PKG_RELEASE) dpkg-buildpackage -nc -us -uc -b --changes-option="-fdebian/realfiles")

install:
	$(PYTHON) setup.py install egg_info -b ""
