Contributing
============

To setup a local development environment and begin working with the Galaxy code, you will need to do have the following 
installed locally:

* Ansible Container 0.2.0+
* Ansible 2.1.1.0+


Checkout the Project and Start a Feature
========================================

Clone the [Galaxy repo](https://github.com/ansible/galaxy) to your local projects folder:

```
cd ~/projects
git clone git@github.com:ansible/galaxy.git
```

Configure git with your name and email so that your commits are correctly associated with your GitHub account:

```
cd ~/projects/galaxy/
git config user.name "Joe Developer"
git config user.email "joe@ansibleworks.com"
```

All development is done on feature branches, and the simplest way to get started is by using Git Flow to start a new 
feature: 

```
cd ~/projects/galaxy
git flow feature start mynewfeature
```

Build and Start the Galaxy Services
===================================

You should already have Docker running and Ansible Container installed. To build the Galaxy images run the following
from the root directory of your Galaxy clone:

```
$ make build
```

After the build completes, you will see the following images in Docker:

```
$ docker images
REPOSITORY                          TAG                 IMAGE ID            CREATED             SIZE
galaxy-django                       20160919015153      cb4deac13890        15 hours ago        619.5 MB
galaxy-django                       latest              cb4deac13890        15 hours ago        619.5 MB
galaxy-gulp                         20160919015153      a9c8919e1a05        16 hours ago        482 MB
galaxy-gulp                         latest              a9c8919e1a05        16 hours ago        482 MB
ansible/ansible-container-builder   0.2                 0e13266a8f4a        31 hours ago        831.3 MB
centos                              7                   980e0e4c79ec        12 days ago         196.8 MB
elasticsearch                       latest              31347bae83b8        2 weeks ago         344.9 MB
python                              2.7                 4c5f5839b372        2 weeks ago         675.3 MB
postgres                            9.4                 7ba4f6e9e5fe        2 weeks ago         264.9 MB
postgres                            latest              6f86882e145d        2 weeks ago         265.9 MB
memcached                           latest              228303902e2e        2 weeks ago         128.2 MB
rabbitmq                            latest              0463354ada4d        3 weeks ago         180.8 MB
```

Start the services by running the following:

```
$ make run
```


Develop, Test and Build
=======================

The following sections describe routine procedures you'll use for developing, testing and building Galaxy.

Vagrant
-------

If you're using Vagrant, you can follow the instructions below as written, but be sure to SSH into the VM with `vagrant ssh` before running any commands that need python or other app dependencies (you can still run git commands from your local machine assuming you have git setup there already). Also, the Vagrant VM installs all dependencies globally, so you can exclude any virtualenv-specific instructions.

Contributing Code
-----------------

Always remember to:

* Use rebase instead of merge (http://git-scm.com/book/en/Git-Branching-Rebasing).
* Use the develop branch for development (unless pushing a hotfix).
* Write unit tests for any non-trivial changes.
* Make sure unit tests pass before pushing your changes.

All original source code files should contain the following header, commented
as appropriate for the given language and immediately following the shebang
line (if present):

    # Copyright (c) 2015 Ansible, Inc.
    # All Rights Reserved.

Basic Development Workflow
---------------------------

Once you have your development environment setup, your normal development workflow should consist of the following steps.

To begin, update the code in your working directory, then refresh your installed third-party dependencies and database schema:

    make rebase
    make refresh

> *NOTE*: `refresh` is a shortcut for `clean`, `requirements`, `develop` and `migrate` targets, and should generally be used anytime you pull new code from the repository.

Restart the servers in the background

    cd ~/projects/galaxy/provisioning
    vagrant ssh
    cd /galaxy_devel
    make servercc

Make your code changes and test them locally, using the API/UI as needed and ensure all unit tests pass:

    make test

Update the list of files to be committed, then make your local commit:

    git add/rm ...
    git commit ...

Finally, rebase your commits on top of any changes made upstream:

    make rebase

Resolve any conflicts and run tests again if upstream changes may have broken
anything.  Finally, push your changes back to the repository.

    make push


Github Authentication
=====================
You can turn on Github authentication for your local environment. Start by creating a superuser account:

    cd ~/projects/galaxy
    python ./manage.py createsuperuser

Log into the administration site at http://localhost:8000/galaxy__admin using the superuser account.

Before changing anything on the administration site, first login into you Github account. Under account settings, choose Applications and click
on the Developer Applications tab.  Provide an application name, set the Homepage URL to `http:\\localhost:8000`, and the Authentication Callback URL to `http://127.0.0.1:8000/accounts/github/login/callback/`. Save your changes.

In your local Galaxy admin site under Social Applications choose Github. Provide the Client Id and Secret Key displayed on your Github account for the
application you created in the step above.

Also, in your local Galaxy admin site click on Sites. There should only be 1 site listed. Click on it and set the Domain Name to `localhost:8000`.

Finally, in /etc/galaxy/settings.py set `ACCOUNT_DEFAULT_HTTP_PROTOCOL="http"`.

Restart the local Galaxy server. 
