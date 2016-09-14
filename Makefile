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

.PHONY: clean rebase push requirements requirements_pypi develop refresh \
	adduser syncdb migrate dbchange dbshell runserver celeryd test \
	test_coverage coverage_html test_ui test_jenkins build_dev \
	release_build release_clean sdist rpm ui_build honcho

# Remove containers, images and ~/.galaxy
clean:
	-docker ps -a --format "{{.Names}}" | grep -e django -e elastic -e postgres -e rabbit -e memcache -e gulp
	-docker rmi --force $(docker images -a --format "{{.Repository}}:{{.Tag}}" | grep galaxy)
	-rm -rf ~/.galaxy

# Refresh development environment after pulling new code.
refresh: clean build run 

# Create and execute database migrations
migrate:
        docker run galaxy-django -v ${PWD}:/galaxy galaxy-manage makemigrations --noinput
        docker run galaxy-django -v ${PWD}:/galaxy galaxy-manage migrate --noinput

# Build Galaxy images 
build: 
	ansible-container --var-file ansible/develop.yml --debug build --from-scratch -- -e"@/ansible-container/ansible/develop.yml"

# Start Galaxy containers
run: 
	ansible-container --var-file ansible/develop.yml run -d memcache; \
	ansible-container --var-file ansible/develop.yml run -d rabbit; \
	ansible-container --var-file ansible/develop.yml run -d postgres; \
	ansible-container --var-file ansible/develop.yml run -d elastic; \
	ansible-container --var-file ansible/develop.yml --debug run django gulp

sdist: clean ui_build
	if [ "$(OFFICIAL)" = "yes" ] ; then \
	   $(PYTHON) setup.py release_build; \
	else \
	   BUILD=$(BUILD) $(PYTHON) setup.py sdist_galaxy; \
	fi

