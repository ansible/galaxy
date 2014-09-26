Contributing
============

Start here if you're contributing to the development of Galaxy. 

Galaxy relies on the following core technologies and frameworks, along with
numerous other smaller libraries and utilities.  Consult the documentation
for each of these projects to better understand how it all works:

* Python 2.6/2.7 (http://docs.python.org/2/)
* Django 1.5 (https://docs.djangoproject.com/en/1.5/)
* Django REST Framework 2.3.x (http://django-rest-framework.org/)
* Django Celery 3.0 (http://docs.celeryproject.org/en/latest/index.html)
* AngularJS 1.x (http://angularjs.org/)

Environment Setup
=================

The following sections describe the steps needed to setup a new development
environment.  Refer to the "Develop, Test and Build" section for commands
you'll run on a regular basic.

Some steps may still be needed on occasion if you're creating a new virtualenv,
destroying your database and starting clean, or switching to a different
version of Ansible.

Prerequisites
-------------

Galaxy primarily targets CentOS 6.4 and Ubuntu 12.04 LTS distributions, but it can
be developed on most any Linux, Unix or OS X operating system.

For CentOS, you should first install EPEL (http://fedoraproject.org/wiki/EPEL):

    sudo rpm -Uvh http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm

You should at least have the following dependencies installed to get started
(package names given are for CentOS 6.3/6.4 and may vary for your OS).

* Git (`git-core`)
* Python 2.6 or 2.7 (`python-devel`)
* Pip (`python-pip`)
* LibYAML (`libyaml`)
* PyYAML (`PyYAML`)
* Paramiko (`python-paramiko`)
* Jinja2 (`python-jinja2`)
* GNU Make (`make`)
* PostgreSQL Server and Python Bindings (`postgresql-server`, `python-psycopg2`)
* Node JS (`nodejs` and `npm`)

To install the above packages on CentOS: 

    sudo yum install git python-devel python-pip libyaml PyYAML python-paramiko python-jinja2 make postgresql-server python-psycopg2 nodejs npm

To install the above packages on Ubuntu: 
    
    sudo apt-get install git python-dev python-pip libyaml-dev python-yaml python-paramiko python-jinja2 make postgresql-9.1 python-psycopg2 nodejs npm

You'll also need to install `less` for NodeJS in order to compile LESS 
files to CSS:

    sudo npm install -g less 

Source Code / Working Directory
-------------------------------

For the rest of this document, we'll assume your working directory will be
`/home/user/projects/galaxy`

> *NOTE:* Since ansible-commander is a private repo, you'll need to setup
> your SSH keys if checking out using SSH. For help, see
> https://help.github.com/articles/generating-ssh-keys.

If just starting, you'll first need to checkout the code from GitHub.

    cd ~/projects/
    git clone git@github.com:ansible/ansible-galaxy.git galaxy

If you'd prefer to use git over HTTPS instead of SSH, replace the URL above
with https://github.com/ansible/ansible-galaxy.git.  In this case you'll
authenticate using your Github username/password instead of SSH keys.

Make sure you've configured git with your name and email so that your commits
are correctly associated with your GitHub account:

    cd ~/projects/galxy/
    git config user.name "Joe Developer"
    git config user.email "joe@ansibleworks.com"


Galaxy Installation
--------------------

Your development environment should be using the latest Ansible code, so you'll
need to install Ansible from source.  If installing into a virtualenv, use one
of the pip methods below.

> *NOTE:* You only need to use *one* of the following options:

To checkout ansible and install from source:

    cd ~/projects/
    git clone https://github.com/ansible/ansible.git
    cd ansible
    sudo make install

To install/update the latest code using pip directly from GitHub:

    sudo pip install -U git+git://github.com/ansible/ansible.git

To install an older released version of Ansible for testing backwards
compatibility:

    sudo pip install ansible==1.2.3

Installing in Development Mode
------------------------------

With the above prerequisites installed and a clone of the repository in
`~/projects/awx/`, you can install AWX in development mode:

    cd ~/projects/awx
    make develop

> This Makefile shortcut is equivalent to running the following command:
> 
>     python setup.py develop

This installation method adds awx to your Python site-packages (or your
virtualenv's site-packages if using a virtualenv) as a link back to your source
checkout, instead of performing a full installation.  As a result, importing
awx from any Python code always refers back to your checkout.

Development mode also installs the `awx-manage` command so that it runs using
your source checkout.

PostgreSQL Configuration
------------------------

In development mode, the AWX project will default to using a SQLite database
file (`awx/awx.sqlite3`) if no other database is configured.  It is recommended
to use PostgreSQL for development (and optionally testing), since it will be
the database used for production installations.

It is also recommended to use a different database for development than for
installing nightly builds locally for testing, since each one will use
different project paths and may also have different database migrations (i.e.
the latest source may have newer migrations that are not yet included in the
most recent nightly build).

If you are configuring a new CentOS system, initialize the PostgreSQL cluster:

    sudo service postgresql initdb

Create your development PostgreSQL user and database using Ansible:

    sudo ansible -i "127.0.0.1," -c local -v -m postgresql_user -U postgres -a "name=awx-dev password=AWXsome1 login_user=postgres" all
    sudo ansible -i "127.0.0.1," -c local -v -m postgresql_db -U postgres -a "name=awx-dev owner=awx-dev login_user=postgres" all

Local Settings
---------------
 
In development mode (i.e. when running from a source checkout), AWX will import
the file `awx/settings/local_settings.py` (if present) to override the default
development settings.

An example file is provided. Make a copy of it and edit as needed:

    cd ~/projects/awx/awx/settings  
    cp local_settings.py.example local_settings.py

Find the DATABASE setting near the top of the file. The username and password
values must match the database, username and password values used when creating
your development database above (awx-dev, awx-dev and AWXsome1).

Any configuration specific to your development environment belongs in
`~/projects/awx/awx/settings/local_settings.py` and will not be committed to
the repository. Do not modify any other settings files found in `awx/settings/`
unless you intend to push those changes to the repository.

*FIXME* How to keep your `local_settings.py` updated as
`local_settings.py.example` changes?

Postgres Authentication on Centos
---------------------------------

For Centos users only, you will need to modify /var/lib/pgsql/data/pg_hba.conf. Assuming you are using postgresql for the first time, replace the default settings with the following: 

    local   all         postgres                          trust

    # TYPE  DATABASE    USER        CIDR-ADDRESS          METHOD
    local   all         all                               md5
    host    all         all         127.0.0.1/32          md5
    host    all         all         ::1/128               md5 

Initialize Database
-------------------

To initialize your development database and apply the latest migrations, run:

    cd ~/projects/awx/
    make migrate

If you are creating a new database, you'll need to create the initial
superuser by running the following command and providing username/password when
prompted:

    make adduser 

Development Web Server
----------------------

Django provides a simple HTTP server for development, which has been enhanced
by the `django-devserver` app. This server normally accepts requests on
http://127.0.0.1:8013/.

To start the development web server, run:

    cd ~/projects/awx/
    make runserver

> *NOTE:* `make runserver` is simply an alias for `python manage.py runserver`.

If you are runnning iptables or another firewall and need to access the
development web server from another host, remember to open port 8013.

The development web server should auto-detect code changes and restart itself;
you should not need to manually restart it unless:

* You've made significant changes to settings or URL patterns.
* You've made a change resulting in a syntax error.

Development Task Engine
-----------------------

AWX uses Celery to run the task engine, which handles running jobs, updating
projects using SCM, and syncing inventory with external sources.

You should normally have both the development web server and the task engine
running simultaneously for AWX to work as expected.

To start the development task engine, run:

    cd ~/projects/awx
    make celeryd

The task engine does not always detect code changes and restart itself
automatically; you will need to manually restart if you have made changes to
your settings, database models or task classes.

Running the Server and Task Engine Automatically (Optional)
-----------------------------------------------------------

If you would like the server and task engine started automatically after a
reboot, add the following to the user's crontab using `crontab -e`: 

    @reboot /usr/bin/python /home/<user>/projects/awx/manage.py runserver > /home/<user>/awx_server.log 2>&1 &
    @reboot /usr/bin/python /home/<user>/projects/awx/manage.py celeryd -l DEBUG -B --autoreload >/home/<user>/celeryd.log 2>&1 &

Over time, the log files may grow quite large, especially `celeryd.log`. On
CentOS add a configuration file to `/etc/logrotate.d` to rotate the output
files. As an example:

    # awx log rotation
    compress

    /home/<user>/awx_server.log {
        rotate 3
        daily
    }

Ubuntu also offers logrotate. Add the above configuration example to
`/etc/logrotate.conf`.

Develop, Test and Build
=======================

After your development environment has been setup, refer to the following
sections for routine procedures you'll use for developing, testing and building
AWX.

Contributing Code
-----------------

Always remember to:

* Use rebase instead of merge (http://git-scm.com/book/en/Git-Branching-Rebasing).
* Use the master branch for development (unless pushing a hotfix).
* Write unit tests for any non-trivial changes.
* Make sure unit tests pass before pushing your changes.

All original source code files should contain the following header, commented
as appropriate for the given language and immediately following the shebang
line (if present):

    # Copyright (c) 2013 AnsibleWorks, Inc.
    # All Rights Reserved.

Basic Development Workflow
---------------------------

Once you have your development environment setup, your normal development
workflow should consist of the following steps.

If using a virtualenv, activate it first:

    workon awx

To begin, update the code in your working directory, then refresh your
installed third-party dependencies and database schema:

    make rebase
    make refresh

> *NOTE*: `refresh` is a shortcut for `clean`, `requirements`, `develop` and 
> `migrate` targets, and should generally be used anytime you pull new code
> from the repository.

If you're not running the servers in the background, then in separate terminals
for each, start your local development web server and task engine:

    make runserver
    make celeryd

Make your code changes and test them locally, using the API/UI as needed and
ensure all unit tests pass:

    make test

Update the list of files to be committed, then make your local commit:

    git add/rm ...
    git commit ...

Finally, rebase your commits on top of any changes made upstream:

    make rebase

Resolve any conflicts and run tests again if upstream changes may have broken
anything.  Finally, push your changes back to the repository.

    make push

Unit Testing for Jenkins
------------------------

The django-jenkins app enables running unit tests and capturing code coverage
in a format suitable for display by Jenkins.  To run the tests:

    cd ~/projects/awx
    make test_jenkins

Unit Testing With Tox
---------------------

Tox provides an automated approach (using multiple virtualenv's) for testing
AWX against different combinations of Python and Django versions.

You'll first need to install tox on your system (or in your development
virtualenv) if you haven't already done so.

    sudo pip install tox

To run tests against multiple Python versions, you'll need to have those
versions installed on your system.

On CentOS 6.4, the default Python version is 2.6.6, and Python 2.7 is not
readily available as a package.  Refer to the following guide to install
`python27` and `python27-devel` packages on CentOS.

> http://linuxsysconfig.com/2013/03/running-multiple-python-versions-on-centos6rhel6sl6/

On Ubuntu 12.04 LTS, the default Python version is 2.7, and Python 2.6 is not
available in the default packages.  Refer the to following PPA to install
`python2.6` and `python26-dev` packages for your system.

> https://launchpad.net/~fkrull/+archive/deadsnakes

Before running tox, your unit tests should already pass on your development
system using your current Python and Django versions and any settings you've
configured in `local_settings.py`.

To run all tox tests (equivalent to running `make test_tox`):

    tox -v

To run only a single test environment (e.g. Python 2.6 + Django 1.4):

    tox -v -e py26-dj14

Edit `tox.ini` to change settings or update dependencies.  For more information
on available tox settings, see http://testrun.org/tox/latest/.

UI Testing With Selenium
------------------------

Testing the UI with Selenium requires the `selenium` Python package and a
recent version of Firefox installed.

To install Selenium:

    sudo pip install selenium

Then run the following to execute UI tests:

    cd ~/projects/awx
    make test_ui

Building AWX Setup Tarball
--------------------------

The setup tarball packages the AWX playbooks (everything in `setup/` directory)
that are used for installing AWX.

    cd ~/projects/awx
    make setup_tarball

The resulting file should be named `awx-setup-<VERSION>-<BUILD>.tar.gz`.

Building AWX RPM Package
------------------------

To build an RPM package, `rpm-build` is required in additional to the normal
development packages.  To install on CentOS:

    sudo yum install rpm-build

Run `make rpm` to build the RPM package.

More information on RPM builds can be found in `docs/build_system.md`.

Building AWX Debian Package
---------------------------

Run `make deb` to build the Debian package.

More information on DEB builds can be found in `docs/build_system.md`.

Testing Nightly Builds
----------------------

Download the latest setup tarball from:

> http://50.116.42.103/awx_nightlies_RTYUIOPOIUYTYU/setup/

Extract the tarball and run the `setup.sh` script with option to use the
nightlies repo:

    ./setup.sh -e "aw_repo_url=http://50.116.42.103/awx_nightlies_RTYUIOPOIUYTYU"

If using CentOS and this is not a fresh installation, run the following to
clean your yum cache:

    sudo yum clean all --enablerepo=ansibleworks-awx

More information on the setup tarball and nightly builds can be found in
`docs/build_system.md`.
