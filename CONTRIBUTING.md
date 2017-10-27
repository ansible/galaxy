# Contributing

Hi! We're excited to have you as a contributor.

Have questions about this document or anything not covered here? Come chat with us at `#ansible-community` on irc.freenode.net.

## Things to know prior to submitting code

- All code submissions are done through pull requests against the `develop` branch.
- You must use `git commit --signoff` for any commit to be merged, and agree that usage of --signoff constitutes agreement with the terms of [DCO 1.1](./DCO_1_1.md).
- Take care to make sure no merge commits are in the submission, and use `git rebase` vs `git merge` for this reason.
- If submitting a large code change, it's a good idea to join the `#ansible-community` channel on irc.freenode.net, and talk about what you would like to do or add first. This not only helps everyone know what's going on, it also helps save time and effort, if the community decides some changes are needed.
- We ask all of our community members and contributors to adhere to the [Ansible code of conduct](http://docs.ansible.com/ansible/latest/community/code_of_conduct.html). If you have questions, or need assistance, please reach out to our community team at [codeofconduct@ansible.com](mailto:codeofconduct@ansible.com)

## Setting up your development environment

The Galaxy development environment workflow and toolchain is based on Docker, and the docker-compose tool, to provide dependencies, services, and databases necessary to run all of the components. It also binds the local source tree into the development container, making it possible to observe and test changes in real time.

### Prerequisites

#### make

For convenience, many of the commands you'll be running to build, start, stop and interact with the development containers have been added to the project [Makefile](./Makefile). Unless you really like typing, you'll want to take advantage of this. Check that you have access to the `make` command, and if not, install the `make` package for your OS.

#### Docker

Prior to starting the development services, you'll need `docker` and `docker-compose`. On Linux, you can generally find these in your distro's packaging, but you may find that Docker themselves maintain a separate repo that tracks more closely to the latest releases.

For macOS and Windows, we recommend [Docker for Mac](https://www.docker.com/docker-mac) and [Docker for Windows](https://www.docker.com/docker-windows)
respectively.

For Linux platforms, refer to the following from Docker:

**Fedora**

> https://docs.docker.com/engine/installation/linux/docker-ce/fedora/

**Centos**

> https://docs.docker.com/engine/installation/linux/docker-ce/centos/

**Ubuntu**

> https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/

**Debian**

> https://docs.docker.com/engine/installation/linux/docker-ce/debian/

**Arch**

> https://wiki.archlinux.org/index.php/Docker

### Build the environment

#### Fork and clone the Galaxy repo

If you have not done so already, you'll need to fork the Galaxy repo on GitHub. For more on how to do this, see [Fork a Repo](https://help.github.com/articles/fork-a-repo/).

#### Build the galaxy-dev image

You're going to run a script that will build the`galaxy-dev` image, which will contain everything needed to run the Galaxy frontend web server, backend Django server, and Celery task runner. Prior to building this image, the script will first build the `galaxy-build` image, which contains all of the required OS packages, Python dependencies, and frontend tools and packages. The `galaxy-build` image is then used as the base image to create `galaxy-dev`.

If you're curious about what actually goes into building the images, you'll find the Dockerfile for `galaxy-build` in [scripts/docker-release](./scripts/docker-release). The actual filename is `Dockerfile.build`. And you'll find the Dockerfile for `galaxy-dev` in [scripts/docker-dev](./scripts/docker-dev).

Run the following to build the image:

```bash
# Set your working directory to the project root
$ cd galaxy

# Start the build process
$ make dev/build
```

Once the build completes, you will the `galaxy-dev` and `galaxy-build` images in your local image cache. Use the `docker images` command to check, as follows:

```bash
$ docker images

REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
galaxy-dev          latest              2f552729e204        22 seconds ago      748MB
galaxy-build        latest              c456f5c226d3        2 minutes ago       568MB
centos              7                   196e0ce0c9fb        6 weeks ago         197MB
```

### Start the containers

We use `docker-compose` to run the containers. If you're curious about the services, and and how they're configured, the compose file is [scripts/compose-dev.yml](./scripts/compose-dev.yml)

#### Quick start

There are a couple different ways to start the development containers. If all of this is new, and you just want to get things going, run the following command to start the containers in an attached mode. All that means is that the STDOUT and STDERR for each container will stream to the STDOUT and STDERR of your terminal session. Your session will be totally consumed with the output, which is OK. Seeing the output lets you know what's actually happening in the containers. To run other commands, and do other things from the your terminal, you'll need to start a second session.

So without further ado, run the following:

```bash
# Set your working directory to the project root
$ cd galaxy

# Start the build process
$ make dev/up
```

Any missing images (i.e., postgresql, memcached, rabbitmq, elasticsearch) will be pulled, and the containers will launch. Aftr the above commands completes, you can take a look at the containers by running `docker ps` in your second terminal session.

#### Running detached

If you prefer to start the containers in detached mode, where they run in the background, run the following command:

```bash
# Set your working directory to the project root
$ cd galaxy

# Start the build process
$ make dev/up_detached
```

#### Running through tmux

If you're familiar with `tmux`, and you would prefer to view the container output through a tmux session, use the following process to launch the containers, and then start the processes within the `galaxy` service using `tmux`.

Start by executing the following command to launch the containers in detached mode, running in the background. Note that there will be no running processes in the `galaxy` service container, because you'll be starting them using `tmux` in the next step.

```bash
# Set your working directory to the project root
$ cd galaxy

# Start the build process
$ make dev/up_tmux
```

Once the above commands completes, you can view the containers by running `docker ps`. The service we're most interested in is `galaxy`, and it's container name will be `galaxy_galaxy_1`. Before we can launch `tmux`, we need to wait for database migrations and other setup to complete. To see what's going on inside the `galaxy` service container, and whether or not the setup is complete, run the following to stream its logging output:

```
$ docker logs -f galaxy_galaxy_1
```

The above will stream the log output to your terminal window. When all the migrations and setup work is done, the output stream will stop, and you'll see output similar to the following:

```
  Applying socialaccount.0003_extra_data_default_dict... OK
+ make build_indexes
Rebuild Custom Indexes
/var/lib/galaxy/venv/bin/python ./manage.py rebuild_galaxy_indexes
/var/lib/galaxy/venv/lib/python2.7/site-packages/maintenance/middleware.py:3: RemovedInDjango19Warning: django.utils.importlib will be removed in Django 1.9.
  from django.utils.importlib import import_module

Rebuild Search Index
/var/lib/galaxy/venv/bin/python ./manage.py rebuild_index --noinput
/var/lib/galaxy/venv/lib/python2.7/site-packages/maintenance/middleware.py:3: RemovedInDjango19Warning: django.utils.importlib will be removed in Django 1.9.
  from django.utils.importlib import import_module

Removing all documents from your index because you said so.
All documents removed.
Indexing 0 roles
+ '[' 1 == 1 ']'
+ scripts/docker-dev/sleep.sh
```

If you see the very last line, `scripts/docker-dev/sleep.sh`, you're ready to start `tmux` and launch the processes inside the `galaxy` service container. Press `Ctrl-c` to stop streaming the logging output, and then run the following:

```bash
# Set your working directory to the project root
$ cd galaxy

# Start tmux
$ make dev/tmux
```

### Accessing the Galaxy web site

After doing all this work, you're anxious to view your shiny new Galaxy site, aren't you? Well, not so fast. As discussed above in [Running through tmux](#running-through-tmux), you'll need to first check to make sure that all the database migrations and setup work completed, and processes are running inside the `galaxy` service container.

Check the output stream from the `galaxy` service container, and look for the completion of database migrations, and the start of the `gulp` web server. If you see output similar to the following, then you know that `gulp` is running and accepting connections:

```
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
```

OK, go ahead. What are you waiting for? You can view your Galaxy site at: [http://localhost:8000](http://localhost:8000).

**NOTE:**

>You won't be able to authenticate until you perform the post build steps for creating an `admin` user and configuring GitHub authentication.

### Post build setup

#### Create an admin user

From the root of the project tree, run `make dev/createsuperuser` to start the creation process. You'll be prompted for the vital details as depicted below:

```
$ make dev/createsuperuser
Create Superuser

Username: admin
Email address: noemail@noemail.com
Password:
Password (again):
Superuser created successfully.
```

The Django admin site can be accessed at [http://localhost:8000/galaxy__admin__site](http://localhost:8000/galaxy__admin__site).

### Connect to GitHub

To log into the development site, you first have to authorize it as a GitHub Oauth Application. You can do this by logging 
into GitHub, going to Personal Settings, choosing `Oauth Applications`, and then doing the following to create a new app:

- Click `Register New Application`
- Set the *Homepage URL* to `http://localhost:8000`. If you're using Docker Machine, replace *localhost* with the IP address 
of the Virtualbox host.
- Set the *Authorization Callback URL* to `http://localhost:8000/accounts/github/login/callback/`. And again, if you're using Docker Machine, replace *localhost* with the IP address of the Virtualbox host.

After you save the new application, access your local Galaxy admin site at [http://localhost:8000/galaxy__admin__site](http://localhost:8000/galaxy__admin__site). If you have not already done so, follow the *Create an Admin User* instructions above.

After logging into the admin site, you'll create a new social application. Start by finding `Social applications` at the bottom of the table, and clicking the *Add* button to its right. On the next screen, set the *provider* to `GitHub`, and enter `GitHub` as the *name*. From the new GitHub Oauth application you just created, copy the *ClientID* value into *Client id*, and copy the *Client Secret* value into *Secret key*. Under *Sites*, add `localhost` to *Chosen sites*. Save the changes.

Log out of the *admin* account, and go back to [http://localhost:8000(http://localhost:8000). Click the GitHub logo under `Log into Galaxy with GitHub`.

### Modifying static assets

The Javascript, CSS and HTML components for the web site can be found in the [galaxy/static](./galaxy/static) folder. Within this folder, the *gulp* service watches for modifications to `less/*.less` stylesheets, and automatically recompiles the CSS and refreshes your browser. It also refreshes your browser whenever changes are made to `js/*/*.js` and `partion/*.html` files.

### Stop services 

To stop all services, run `make dev/down`.

### Submitting Code

Code submissions are accepted via pull requests (PR), and they are always welcome! We may not accept them all, but we are 
always happy to review and discuss them with you.

Before submitting a large pull request for a new feature, we suggest opening an issue to discuss the feature prior to 
submission.

We reserve the right to reject submissions that are not a good fit for the project, or not in keeping with the intended 
direction of the project. If you are unsure as to whether a feature is a good fit, take the time to open an issue.

Please observe the following when submitting a PR:

* Rebase instead of merge (http://git-scm.com/book/en/Git-Branching-Rebasing).
* Follow the Git Flow branching model and develop in a feature branch
* Limit the scope of a submission to a single feature or bug fix.
* Before embarking on a large feature, open an issue and submit the feature for review by the community

