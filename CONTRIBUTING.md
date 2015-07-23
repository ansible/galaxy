Contributing
============

Start here if you're contributing to the development of Galaxy. 

Galaxy relies on the following core technologies and frameworks, along with numerous other smaller libraries and utilities. Consult the documentation for each of these projects to better understand how it all works:

* Python 2.7 (http://docs.python.org/2/)
* Django 1.8.3 https://docs.djangoproject.com/en/1.5/)
* Django REST Framework 2.3.x (http://django-rest-framework.org/)
* Django Celery 3.0 (http://docs.celeryproject.org/en/latest/index.html)
* AngularJS 1.x (http://angularjs.org/)


Prerequisites
=============
Contributing to Galaxy relies on the creation of VM using Vagrant, Virtualbox and Ansible. Refer to the product sites of each for downloads and instructions:

[Ansible](http://docs.ansible.com/ansible/intro_installation.html)
[Virtualbox](https://www.virtualbox.org/wiki/Downloads)
[Vagrant](http://www.vagrantup.com)


Project Checkout
================

Clone the [Galaxy repo](https://github.com/ansible/galaxy) to your local projects folder:

```
cd ~/projects
git clone git@github.com:ansible/galaxy.git
```

Configure git with your name and email so that your commits are correctly associated with your GitHub account:

```
cd ~/projects/galxy/
git config user.name "Joe Developer"
git config user.email "joe@ansibleworks.com"
```

All development is done in the 'develop' branch. To checkout the 'develop' branch: 

```
cd ~/projects/galaxy
git checkout develop
``` 

Environment Setup
=================

The following sections provide the steps to creating a new development VM. Refer to the "Develop, Test and Build" section for commands you'll run on a regular basis.


Vagrant
-------

To get up and running quickly the `provisioning` folder provides a Vagrant configuration to quickly spin up a VM.

Make sure you have [Virtualbox](https://www.virtualbox.org/wiki/Downloads), [Vagrant](http://www.vagrantup.com), and [Ansible](http://docs.ansible.com) installed. Then provision the VM from within the project 'provisioning' folder. The following assumes galaxy was cloned to ~/projects/galaxy: 

```
cd ~/projects/galaxy/provisioning
vagrant box add chef/centos-7.0
vagrant up
```

To start the server ssh into the VM and run the following: 

```
cd ~/projets/galaxy/provisioning
vagrant ssh
cd /galaxy_devel
make servercc 
```
> *NOTE*: If you're not using iTerm2 on a MacBook, replace `servercc` with `server`. 

> *NOTE*: If you're using the `vagrant-kvm` driver and have trouble accessing `http://localhost:8000` then you can run `python manage.py runserver 0.0.0.0:8000` in the guest VM, and on the host use `vagrant ssh-config` to see the IP address of the VM. Browse to that IP on port 8000 to access the site.

On your local computer browse to <http://localhost:8000>, and you will see a running Galaxy.

The Vagrantfile mounts the root of the galaxy directory as a share in the VM accessible as /galaxy_devel. This means that you can continue to edit code on your local machine like you normally would and changes will reflect in the VM.

All dependencies are installed and the database is setup via the Ansible provisioner. It uses the play.yml playbook found in the provisioning folder.

Refer to the [Develop, Test and Build](#Develop,_Test_and_Build) section for further instructions on running with Vagrant.


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
