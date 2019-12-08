=================
Contributor Guide
=================

Hi! We're excited to have you as a contributor.

Have questions about this document or anything not covered here?
Come chat with us at ``#ansible-community`` on ``irc.freenode.net``.

Things to know prior to submitting code
=======================================

* All code submissions are done through pull requests
  against the ``devel`` branch.
* You must use ``git commit --signoff`` for any commit to be merged,
  and agree that usage of ``--signoff`` constitutes agreement with the terms
  of `DCO 1.1 <https://github.com/ansible/galaxy/blob/devel/DCO_1_1.md>`_.
* Take care to make sure no merge commits are in the submission,
  and use `git rebase` vs `git merge` for this reason.
* If submitting a large code change, it's a good idea to join the
  ``#ansible-community`` channel on ``irc.freenode.net``, and talk about
  what you would like to do or add first.
  This not only helps everyone know what's going on, it also helps save
  time and effort, if the community decides some changes are needed.
* We ask all of our community members and contributors to adhere to the
  `Ansible code of conduct <http://docs.ansible.com/ansible/latest/community/code_of_conduct.html>`_.
  If you have questions, or need assistance, please reach out to our community
  team at codeofconduct@ansible.com.

Setting up your development environment
==========================================

The Galaxy development environment workflow and toolchain is based on Docker,
and the ``docker-compose`` tool, to provide dependencies, services,
and databases necessary to run all of the components.
It also binds the local source tree into the development container,
making it possible to observe and test changes in real time.

Prerequisites
-----------------

make
^^^^

For convenience, many of the commands you'll be running to build,
start, stop and interact with the development containers have been added
to the project `Makefile <https://github.com/ansible/galaxy/blob/devel/Makefile>`_.
Unless you really like typing, you'll want to take advantage of this.
Check that you have access to the ``make`` command, and if not,
install the ``make`` package for your OS.

Docker
^^^^^^

Prior to starting the development services, you'll need ``docker``
and ``docker-compose``. On Linux, you can generally find these in your
distro's packaging, but you may find that Docker themselves maintain
a separate repo that tracks more closely to the latest releases.

For MacOS and Windows, we recommend `Docker for Mac <https://www.docker.com/docker-mac>`_
and `Docker for Windows <https://www.docker.com/docker-windows>`_ respectively.

For Linux platforms, refer to the following from Docker:

**Fedora**

https://docs.docker.com/engine/installation/linux/docker-ce/fedora/

**Centos**

https://docs.docker.com/engine/installation/linux/docker-ce/centos/

**Ubuntu**

https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/

**Debian**

https://docs.docker.com/engine/installation/linux/docker-ce/debian/

**Arch**

https://wiki.archlinux.org/index.php/Docker

Build the environment
---------------------

Fork and clone the Galaxy repo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have not done so already, you'll need to fork the Galaxy repo on GitHub.
For more on how to do this, see `Fork a Repo <https://help.github.com/articles/fork-a-repo/>`_.

Build the galaxy-dev image
^^^^^^^^^^^^^^^^^^^^^^^^^^

The first step to running a local Galaxy instance is building the images.
You're going to run a script that will build the ``galaxy-dev`` image,
which will contain everything needed to run the Galaxy frontend web server,
backend Django server, and Celery task runner.

.. FIXME: The following paragraph is out of date.

Prior to building this image, the script will first build the ``galaxy-build``
image, which contains all of the required OS packages, Python dependencies,
and frontend tools and packages. The ``galaxy-build`` image is then used
as the base image to create ``galaxy-dev``.

If you're curious about what actually goes into building the images,
you'll find the ``Dockerfile`` for ``galaxy-build`` in
`scripts/docker/release <https://github.com/ansible/galaxy/tree/devel/scripts/docker/release>`_.
The actual filename is ``Dockerfile.build``. And you'll find the Dockerfile
for ``galaxy-dev`` in `scripts/docker/dev <https://github.com/ansible/galaxy/tree/devel/scripts/docker/dev>`_.

Run the following to build the image:

.. code-block:: console

    ## Set your working directory to the project root
    $ cd galaxy

    ## Start the build process
    $ make dev/build

Once the build completes, you will have the ``galaxy-dev`` and ``galaxy-build``
images in your local image cache. Use the ``docker images`` command to check,
as follows:

.. code-block:: console

    $ docker images

    REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
    galaxy-dev          latest              2f552729e204        22 seconds ago      748MB
    galaxy-build        latest              c456f5c226d3        2 minutes ago       568MB
    centos              7                   196e0ce0c9fb        6 weeks ago         197MB

Start the containers
--------------------

We use ``docker-compose`` to run the containers. If you're curious about
the services, and and how they're configured, the compose file is
`scripts/docker/dev/compose.yml <https://github.com/ansible/galaxy/blob/devel/scripts/docker/dev/compose.yml>`_.

.. _contributing-quick-start:

Quick start
^^^^^^^^^^^

There are a couple different ways to start the development containers.
If all of this is new, and you just want to get things going, run the
following command to start the containers in an attached mode.
All that means is that the ``stdout`` and ``stderr`` for each container will
stream to the ``stdout`` and ``stderr`` of your terminal session.

After running the command, your session will be totally consumed with the
output, which is OK. Seeing the output lets you know what's actually
happening in the containers. So afterwards, to run additional commands
from your terminal, you'll need to start a second session.

So without further ado, run the following:

.. code-block:: console

    ## Set your working directory to the project root
    $ cd galaxy

    ## Start the build process
    $ make dev/up

Any missing images (i.e. postgresql, rabbitmq, prometheus, influxdb, grafana)
will be pulled. Getting all the images downloaded may take a few minutes.
Once all the images are available, the containers will launch.

After the above commands complete, you can take a look at the containers by
running ``docker ps`` in your second terminal session:

.. code-block:: console

    $ docker ps

    CONTAINER ID        IMAGE                          COMMAND                  CREATED             STATUS              PORTS                                NAMES
    b76488f94890        galaxy-dev:latest              "/entrypoint.sh /g..."   2 minutes ago       Up 2 minutes        0.0.0.0:8000->8000/tcp               galaxy_galaxy_1
    dfe97d19197e        centos/postgresql-95-centos7   "container-entrypo..."   22 hours ago        Up 2 minutes        0.0.0.0:2345->5432/tcp               galaxy_postgres_1
    fd3dd5f663f2        rabbitmq:latest                "docker-entrypoint..."   22 hours ago        Up 2 minutes        4369/tcp, 5671-5672/tcp, 25672/tcp   galaxy_rabbitmq_1
    9561d0cea1ec        prom/prometheus:latest         "/bin/prometheus -..."   2 minutes ago       Up 2 minutes        0.0.0.0:9090->9090/tcp               galaxy_prometheus_1
    21e8b688f2ab        influxdb:latest                "/entrypoint.sh in..."   22 hours ago        Up 2 minutes        0.0.0.0:8086->8086/tcp               galaxy_influxdb_1
    92186c792b4d        grafana/grafana:latest         "/run.sh"                2 minutes ago       Up 2 minutes        0.0.0.0:3000->3000/tcp               galaxy_grafana_1

Running detached
^^^^^^^^^^^^^^^^

If you prefer to start the containers in detached mode, where they run in the
background, run the following command:

.. code-block:: console

    ## Set your working directory to the project root
    $ cd galaxy

    ## Start the build process
    $ make dev/up_detached


Since the ``stdout`` and ``stderr`` are not streaming to your terminal
session, you'll need to use the ``docker logs`` command to view logging output.
As pictured above in `Quick start`_, use ``docker ps`` to see
the list of running containers, then use ``docker logs -f <container name>``
to stream a container's output. Use ``<Ctrl-C>`` to stop the streaming output.

Running through tmux
^^^^^^^^^^^^^^^^^^^^

If you're familiar with ``tmux``, and you would prefer to view the container
output through a ``tmux`` session, use the following 2-step process to launch
the containers, and then access the processes within the ``galaxy`` service
using ``tmux``.

#. Execute the following to launch the containers in detached mode,
   running in the background.

   .. code-block:: console

        ## Set your working directory to the project root
        $ cd galaxy

        ## Start the build process
        $ make dev/up_detached

#. Once the above command is complete, you can view the containers
   by running ``docker ps``. The service we're most interested in is
   ``galaxy``, and it's container name will be ``galaxy_galaxy_1``.
   Before we can launch ``tmux``, we need to wait for database migrations and
   other setup to complete. To see what's going on inside the ``galaxy``
   service container, and whether or not the setup is complete,
   run the following to stream its logging output:

   .. code-block:: console

        $ docker logs -f galaxy_galaxy_1

   The above will stream the log output to your terminal window.
   When all the migrations and setup work is done, the output stream will stop,
   and you'll see output similar to the following:

   .. code-block:: none

          Applying main.0120_repository_quality_score_date... OK
          Applying main.0121_userpreferences... OK
          Applying main.0122_auto_20181015_1802... OK
          Applying main.0123_fix_importtaskmessage_constraints... OK
          Applying main.0124_auto_20181210_1433... OK
          Applying main.0125_collection_base... OK
          Applying sessions.0001_initial... OK
          Applying sites.0001_initial... OK
          Applying sites.0002_alter_domain_unique... OK
          Applying socialaccount.0001_initial... OK
          Applying socialaccount.0002_token_max_lengths... OK
          Applying socialaccount.0003_extra_data_default_dict... OK
        Starting tmux...

   Once you see the very last line, ``Starting tmux...``,
   you're ready for the next step.

#. Now you'll start ``tmux`` and launch the processes inside the ``galaxy``
   service container by running the following. If you're streaming the
   logging output still, use ``<Ctrl-C>`` to stop the stream.

   .. code-block:: console

        ## Start tmux
        $ make dev/attach

Accessing the Galaxy web site
-----------------------------

After doing all this work, you're anxious to view your shiny new Galaxy site,
aren't you? Well, not so fast. As discussed above in `Running through tmux`_,
you'll need to first check to make sure that all the database migrations
and setup work completed, and processes are running inside the ``galaxy``
service container.

Check the output stream from the ``galaxy`` service container, and look for
the completion of database migrations, and the start of the ``gulp`` web server.
If you see output similar to the following, then you know that ``gulp`` is
running and accepting connections:

.. code-block:: none

    [03:10:00] Using gulpfile /galaxy/gulpfile.js
    [03:10:01] Starting 'less'...
    [03:10:01] Starting 'server'...
    [HPM] Proxy created: /  ->  http://localhost:8888
    [03:10:01] Finished 'server' after 130 ms
    [03:10:01] Starting 'watch'...
    [03:10:03] Finished 'watch' after 2.06 s
    [Browsersync] Access URLs:
     -----------------------------------
           Local: http://localhost:8000
        External: http://172.18.0.6:8000
     -----------------------------------
              UI: http://localhost:3001
     UI External: http://172.18.0.6:3001
     -----------------------------------
    [Browsersync] Serving files from: /galaxy
    [03:10:04] Finished 'less' after 3.23 s
    [03:10:04] Starting 'default'...
    [03:10:04] Finished 'default' after 108 μs

OK, go for it! Your Galaxy web site is available at: `http://localhost:8000 <http://localhost:8000>`_.

.. note:: You won't be able to authenticate until you perform the post build
          steps for creating an `admin` user and configuring GitHub authentication.

Post build setup
----------------

Create an admin user
^^^^^^^^^^^^^^^^^^^^

From the root of the project tree, run ``make dev/createsuperuser`` to start
the creation process. You'll be prompted for the vital details as depicted below:

.. code-block:: console

    $ make dev/createsuperuser
    Create Superuser

    Username: admin
    Email address: noemail@noemail.com
    Password:
    Password (again):
    Superuser created successfully.

The Django admin site can be accessed at `http://localhost:8000/admin <http://localhost:8000/admin>`_.

Create an admin token
^^^^^^^^^^^^^^^^^^^^^

From the root of the project tree, run ``make USERNAME=admin dev/createusertoken`` to start
the creation process. You'll see the details as depicted below:

.. code-block:: console

    $ make USERNAME=admin dev/createusertoken
    Create user token
    Generated token ea40be900297ece22f782be651144251f59ac487 for user admin

Connect to GitHub
-----------------

To log into the development site, you first have to authorize it as a
GitHub Oauth Application. You can do this by logging into GitHub,
going to Personal Settings, choosing ``OAuth Applications``,
and then doing the following to create a new app:

* Click **Register New Application**.
* Set the **Homepage URL** to ``http://localhost:8000``.
* Set the **Authorization Callback URL** to ``http://localhost:8000/accounts/github/login/callback/``.

Log into your Galaxy admin site
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After you save the new application, access your local Galaxy admin site
at `http://localhost:8000/admin`_, and log in using the admin user you created
above in [Create admin user](#create-admin-user)

Update the site name
^^^^^^^^^^^^^^^^^^^^

Click on **Sites**. You'll see one site defined, ``example.com``.
Click on ``example.com`` to modify it. On the next page, change both the
**Domain Name** and **Display Name** from ``example.com`` to ``localhost``.
Click the **Save** button.

Create a new social application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Next, create a new social application. Start by finding ``Social applications``
at the bottom of the list, on the admin site home page.
Click the **Add** button to its right, and on the next page, complete the
following to configure the new application:

* Set the **Provider** to ``GitHub``.
* Enter ``GitHub`` as the **Name**.
* From the new GitHub OAuth application you just created, copy the
  **ClientID** value into **Client id**.
* Copy the **Client Secret** value into **Secret key**.
* Under **Sites**, add ``localhost`` to **Chosen sites**. Save the changes.

Now test the authentication. Log out of your admin account, and go back to the
home page at `http://localhost:8000`_. Now log in using your GitHub account by
clicking the GitHub logo under **Log into Galaxy with GitHub**.

Modifying static assets
-----------------------

.. FIXME: galaxy/static folder was removed

The Javascript, CSS and HTML components for the web site can be found in the
`galaxy/static <https://github.com/ansible/galaxy/tree/devel/galaxy/static>`_ folder. Within this folder,
the ``gulp`` service watches for modifications to ``less/*.less`` stylesheets,
and automatically recompiles the CSS and refreshes your browser.
It also refreshes your browser whenever changes are made
to ``js/*/*.js`` and ``partion/*.html`` files.

Stop services
-------------

To stop all services, run ``make dev/down``.

Validating your changes
-----------------------

Once you have Galaxy composed and running, you may also run
different commands to check your changes.

To do this you need Galaxy running in detached state or run commands from
a separate terminal session.

Full list of commands is available in Makefile, however we want to highlight
the most useful here.

Linting your code
^^^^^^^^^^^^^^^^^

To run lint checks against Python sources, execute:

.. code-block:: console

    $ make dev/flake8

To run lint checks against JavaScript/TypeScript sources, execute:

.. code-block:: console

    $ make dev/jslint

Formatting your code
^^^^^^^^^^^^^^^^^^^^

We use prettier to enforce code formatting for all of our TypeScript and less files.
To automatically format your Angular code run:

.. code-block:: console

    $ make dev/prettier

Unformatted code will cause the Travis build to fail when you push your changes to
GitHub.

It's recommended that you set up prettier on your editor if you're making lots of
changes to anything in ``galaxyui/``. Prettier is supported by most major editors
and you can find more `information about that here <https://prettier.io/docs/en/editors.html>`_.

Our prettier configuration can be found at ``galaxyui/.prettierrc.yaml``. Please
use it when setting up your editor.

Testing your code
^^^^^^^^^^^^^^^^^

To run unit and functional tests against execute:

.. code-block:: console

    $ make dev/test

This command will test Python code and also will produce test coverage reports.

There are 3 kinds of reports produced:

* Console report, that shows coverage in console
* Static HTML files located in htmlcov with htmlcov/index.html as entry point
* ``coverage.xml``, that may be used by your IDE or text editor.

These files are not part of git repository and will not be commited.

If you use VSCode as your editor and want to integrate ``coverage.xml``
report and highlight code accordingly, then you may be interested in
`Coverage Gutters <https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters>`_
plugin. In order to make it working, you need to install it and add following lines into your VSCode configuration:

.. code-block:: none

    "coverage-gutters.xmlname": "coverage.xml",

If you use PyCharm Professional, then you may configure it according to the
`Code Coverage <https://www.jetbrains.com/help/pycharm/code-coverage.html>`_ guide.

Static HTML files may be used simply by opening them in your favourite web browser.

Upgrading dependencies
^^^^^^^^^^^^^^^^^^^^^^

Galaxy uses pinned dependencies (aka lock-files) to provide reproducible
environment installations. These files are compiled from requirements files
by using ``pip-tools`` package. This package is not included into project
dependencies and should be installed manually.

To update project requirements you should edit ``*.in`` files stored in ``requirements/`` directory.
Files ``requirements.in`` and ``dev-requirements.in`` are used for specifying
common and development requirements respectively.

Then you should generate lock file for the requirements file you modified by
calling the following command:

.. code-block:: none

  $ pip-tools --output requirements/<filename>.txt requirements/<filename>.in

And then commit the both files to git.


Commiting
---------

Once you have all lint and tests passed and you are ready to commit your patch
and propose pull request, install pre-commit hook, provided by this repository:

.. code-block:: console

    $ cp pre-commit .git/hooks/pre-commit

Don't forget to commit your code with ``git commit --signoff`` as described in
the top of this document and follow other guidelines.

Thank you for your contribution!
