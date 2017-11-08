# Installing Galaxy

This document provides a guide for installing Galaxy.

## Table of contents

- [Getting started](#getting-started)
  - [Clone the repo](#clone-the-repo)
  - [Prerequisites](#prerequisites)
  - [Official vs Building Images](#official-vs-building-images)
- [OpenShift](#openshift)
- [Docker](#docker)
  - [Prerequisites](#prerequisites)
  - [Pre-build steps](#pre-build-steps)
    - [Deploying to a remote host](#deploying-to-a-remote-host)
    - [Inventory variables](#inventory-variables)
      - [Docker registry](#docker-registry)
      - [PostgreSQL](#postgresql)
      - [Elasticsearch](#elasticsearch)
      - [Proxy settings](#proxy-settings)
  - [Start the build](#start-the-build)
  - [Post build](#post-build)
  - [Accessing Galaxy](#accessing-galaxy)
  - [Configure GitHub Oauth](#configure-github-oauth)
  - [Load platforms](#load-platforms)
  - [Stop containers](#stop-containers)

## Getting started

### Clone the repo

If you have not already done so, you will need to clone, or create a local copy, of the [Galaxy repo](https://github.com/ansible/galaxy). For more on how to clone the repo, view [git clone help](https://git-scm.com/docs/git-clone).

Once you have a local copy, run commands within the root of the project tree.

### Prerequisites

Before you can run a deployment, you'll need the following installed in your local environment:

- [Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html) Requires Version 2.3+
- [Docker](https://docs.docker.com/engine/installation/)
- [docker-py](https://github.com/docker/docker-py) Python module
- [GNU Make](https://www.gnu.org/software/make/)
- [Git](https://git-scm.com/)

### Official vs Building Images

When installing Galaxy you have the option of building your own images or using the images provided on DockerHub (see [galaxy](https://hub.docker.com/r/ansible/galaxy/))

This is controlled by the following variables in the `inventory` file:

```
dockerhub_base=ansible
dockerhub_version=latest
```

If these variables are present, then the deployment will use the hosted images. And if not present, images will be built during the install.

*dockerhub_base*

> The base location on DockerHub where the images are hosted (by default this pulls container the image named `ansible/galaxy:tag`)

*dockerhub_version*

> Multiple versions are available. `latest` always pulls the most recent stable release, and `develop` pulls the latest development images. You can also provide a specific release version.

### Custom branding 

When building custom images, you can replace or overwrite any of the Galaxy branding and home page content with your own by setting the value of *custom_branding_path* in the inventory file.

Provide a path to a directory containing the following subdirectories: templates, img, less, partials. During the image build process, the contents of these subdirectories will be automatically copied into the corresponding subdirectories under [galaxy/static](./galaxy/static).

## OpenShift

Instructions coming soon. Please check back.

## Docker

### Prerequisites

You will need the following installed on the host where Galaxy will be deployed:

- [Docker](https://docs.docker.com/engine/installation/)
- [docker-py](https://github.com/docker/docker-py) Python module

Note: After installing Docker, the Docker service must be started. 

### Pre-build steps

#### Deploying to a remote host

By default, the delivered [installer/inventory](./installer/inventory) file will deploy Galaxy to the local host. It is possible; however, to deploy to a remote host. The [installer/galaxy.yml](./installer/galaxy.yml) playbook can be used to build images on the local host, and ship the built images to, and run deployment tasks on, a remote host. To do this, modify the [installer/inventory](./installer/inventory) file, by commenting out `localhost`, and adding the remote host.

For example, suppose you wish to build images locally on your CI/CD host, and deploy them to a remote host named *galaxy-server*. To do this, add *galaxy-server* to the [installer/inventory](./installer/inventory) file, and comment out or remove `localhost`, as demonstrated by the following:

```yaml
# localhost ansible_connection=local
galaxy-server

[all:vars]
...
```

In the above example, image build tasks will be delegated to `localhost`, which is typically where the clone of the Galaxy project exists. Built images will be archived, copied to remote host, and imported into the remote Docker image cache. Tasks to start the Galaxy containers will then execute on the remote host.

If you choose to use the official images, then the remote host will be the one to pull those images.

**Note**

> You may also want to set additional variables to control how Ansible connects to the host. For more information about this, view [Behavioral Inventory Parameters](http://docs.ansible.com/ansible/latest/intro_inventory.html#id12).

> As mentioned above, in [Prerequisites](#prerequisites-1), the prerequisites are required on the remote host.

> When deploying to a remote host, the playbook does not execute tasks with the `become` option. For this reason, make sure the user that connects to the remote host has privileges to run the `docker` command. This typically means that non-privileged users need to be part of the `docker` group.


#### Inventory variables

Before starting the build process, review the [inventory](./installer/inventory) file, and uncomment and provide values for the following variables found in the `[all:vars]` section:

*postgres_data_dir*

> If you're using the default PostgreSQL container (see [PostgreSQL](#postgresql-1) below), provide a path that can be mounted to the container, and where the database can be persisted.

*elastic_data_dir*

> When using the default Elastic conainer, provide a path that can be mounted to the conatiner, and where index data can be persisted.

*host_port*

> Provide a port number that can be mapped from the Docker daemon host to the web server running inside the Galaxy container. Defaults to *80*.


#### Docker registry

If you wish to tag and push built images to a Docker registry, set the following variables in the inventory file:

*docker_registry*

> IP address and port, or URL, for accessing a registry.

*docker_registry_repository*

> Namespace to use when pushing and pulling images to and from the registry. Defaults to *galaxy*.

*docker_registry_username*

> Username of the user that will push images to the registry. Defaults to *developer*.

*docker_remove_local_images*

> Due to the way that the docker_image module behaves, images will not be pushed to a remote repository if they are present locally.  Set this to delete local versions of the images that will be pushed to the remote.  This will fail if containers are currently running from those images.

**Note**

> These settings are ignored, if using official images.


#### Proxy settings

*http_proxy*

> IP address and port, or URL, for using an http_proxy.

*https_proxy*

> IP address and port, or URL, for using an https_proxy.

*no_proxy*

> Exclude IP address or URL from the proxy.

#### PostgreSQL

Galaxy requires access to a PostgreSQL database, and by default, one will be created and deployed in a container, and data will be persisted to a host volume. In this scenario, you must set the value of `postgres_data_dir` to a path that can be mounted to the container. When the container is stopped, the database files will still exist in the specified path.

If you wish to use an external database, in the inventory file, set the value of `pg_hostname`, and update `pg_username`, `pg_password`, `pg_database`, and `pg_port` with the connection information.

#### Elasticsearch

Galaxy requires access to an Elasticsearch instance, and by default, one will be created and deployed in a container, and data will be persisted to a host volume. In this scenario, you must set the value of `elastic_data_dir` to a path that can be mounted to the container. When the container is stopped, the index files will still exist in the specified path.

If you wish to use an external Elasticsearch cluster, in the inventory file, set the value of `elastic_hostname` and `elastic_port`.

### Start the build

If you are not pushing images to a Docker registry, start the build by running the following:

```bash
# Set the working directory to installer
$ cd installer

# Run the Ansible playbook
$ ansible-playbook -i inventory galaxy.yml --tags start
```

If you're pushing built images to a repository, then use the `-e` option to pass the registry password as follows, replacing *password* with the password of the username assigned to `docker_registry_username` (note that you will also need to remove `dockerhub_base` and `dockerhub_version` from the inventory file):

```bash
# Set the working directory to installer
$ cd installer

# Run the Ansible playbook
$ ansible-playbook -i inventory galaxy.yml -e docker_registry_password=password --tags start
```

### Post build

After the playbook run completes, Docker will report up to 5 running containers. If you chose to use an existing PostgresSQL database, then it will report 4. You can view the running containers using the `docker ps` command, as follows:

```bash
CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS              PORTS                                NAMES
51c4a143a99e        ansible/galaxy:develop   "/entrypoint.sh /b..."   7 seconds ago       Up 5 seconds        8000/tcp                             galaxy_worker_1
c223afe43b3a        ansible/galaxy:develop   "/entrypoint.sh /b..."   9 seconds ago       Up 6 seconds        0.0.0.0:80->8000/tcp                 galaxy_web_1
85069688151f        postgres:9.5.4           "/docker-entrypoin..."   11 seconds ago      Up 8 seconds        5432/tcp                             galaxy_postgres_1
46bb2709f47f        memcached:latest         "docker-entrypoint..."   11 seconds ago      Up 9 seconds        11211/tcp                            galaxy_memcache_1
5e984e46d5ac        elasticsearch:2.4.1      "/docker-entrypoin..."   11 seconds ago      Up 8 seconds        9200/tcp, 9300/tcp                   galaxy_elastic_1
4e627b9e8558        rabbitmq:latest          "docker-entrypoint..."   11 seconds ago      Up 9 seconds        4369/tcp, 5671-5672/tcp, 25672/tcp   galaxy_rabbitmq_1
```

Immediately after the containers start, the *galaxy_web* container will perform some setup tasks, including database migrations. These tasks need to complete before the web interface can be accessed. To monitor the progress, you can follow the container's STDOUT by running the following:

```bash
# Tail the the log
$ docker logs -f galaxy_web_1
```

You will see output similar to the following:

```bash
$ docker logs galaxy_web_1
2017-11-06 14:38:06,365 INFO waitenv: manage.py waitenv...
2017-11-06 14:38:06,377 INFO waitenv: Waiting on postgres:5432
2017-11-06 14:38:30,419 INFO waitenv: Waiting on rabbitmq:5672
2017-11-06 14:38:30,423 INFO waitenv: Waiting on memcache:11211
2017-11-06 14:38:30,431 INFO waitenv: Waiting on elastic:9200
Operations to perform:
  Synchronize unmigrated apps: google, staticfiles, twitter, messages, allauth, github, maintenance, rest_framework, haystack, bootstrapform
  Apply all migrations: authtoken, account, sessions, admin, djcelery, sites, auth, contenttypes, accounts, main, socialaccount
Synchronizing apps without migrations:
  Creating tables...
    Creating table maintenance_maintenancewindow
    Running deferred SQL...
  Installing custom SQL...
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying accounts.0001_initial... OK
  Applying account.0001_initial... OK
  Applying account.0002_email_max_length... OK
  Applying accounts.0002_auto_20150803_1328... OK
  Applying accounts.0003_auto_20151125_0840... OK
  Applying accounts.0004_customuser_cache_refreshed... OK
...
```

Once migrations complete, you will see the `gunicorn` process start, indicating that migrations have completed, and web access is available:

```bash
[2017-11-06 19:39:03 +0000] [24] [INFO] Starting gunicorn 19.7.1
[2017-11-06 19:39:03 +0000] [24] [INFO] Listening at: http://0.0.0.0:8000 (24)
[2017-11-06 19:39:03 +0000] [24] [INFO] Using worker: gevent
[2017-11-06 19:39:03 +0000] [29] [INFO] Booting worker with pid: 29
[2017-11-06 19:39:03 +0000] [30] [INFO] Booting worker with pid: 30
...
```

### Accessing Galaxy

The Galaxy web server is accessible on the deployment host, using the *host_port* value set in the *inventory* file. The default URL is [http://localhost](http://localhost).

### Configure GitHub Oauth

In order to access Galaxy using GitHub Oauth, you'll need to complete create an admin user, create an Oauth application on GitHub, and use the Galaxy admin site to connect your new Galaxy site to the Ouath application on GitHub. The following section details the steps you'll need to complete. 

#### Create an admin account

You'll first need to create an admin user by performing the following:

- Start an interactive sessoin on the web container by running the command: `docker exec -it galaxy_web_1 /bin/bash`
- Within the web container run the following: `${VENV_BIN}/galaxy-manage createsuperuser`
- You will be prompted for a username, email address and password, and asked to confirm the password. The email address is not important, any value that looks like a valid email will work. 
- Once the account is created, use the `exit` command to termintate the session. 

#### Set the site name

Log into the admin site at [localhost/admin](http://localhost/admin), using the admin account you created in the step above. 

Click on `Sites`, and click on `example.com`. On the next page, change `example.com` to `localhost` or your actual domain name. Change both the `Domain name` and `Display name` fields, and click the `Save` button.

#### Create a GitHub social application

In order to log into your Galaxy site using GitHub credentials, you'll need to create an Oauth application on the GitHub site, and connect it to your Galaxy site. 

Start by logging into your GitHub developer account, and creating a new Oauth application. For more on how to do this, view [the GitHub developer guide](https://developer.github.com/apps/building-integrations/setting-up-and-registering-oauth-apps/registering-oauth-apps/).

Once you have an Oauth application, set the callback URL to `http://localhost/accounts/github/login/callback/`. You can use `localhost`, or replace it with the domain name of your Galaxy site.

Within the local Galaxy admin site, you'll add a new social application, by clicking the `Add` button to the right of `Social Applications` at the bottom of the page. 

Within the new social application, set the `Provider` to `GitHub`, and the `Name` to `GitHub`. From your Oauth application on GitHub, copy the `Client Id` and `Client Secret` to the `Client Id` and `Secret Key` fields respectively. Under `Sites`, move your site name from `Available Sites` to the list of `Chosen Sites`. And finally, click the `Save` button to save your changes.

Log out of your admin account on your Galaxy site, return to the [home page](http://localhost), and click the Octocat logo to log in using your GitHub account.

### Load platforms

If you want to poplulate the Platforms data, run the following:

```bash
# Start an interactive session with the web container
$ docker exec -it galaxy_web_1 /bin/bash 

# Set the working directory
$ cd /galaxy/test-data

# Load platforms
$ ${VENV_BIN}/galaxy-manage loaddata platform.json
```

### Stop containers

To stop the Galaxy containers, run the following:

```bash
# Set the working directory to installer
$ cd installer

# Run the Ansible playbook
$ ansible-playbook -i inventory galaxy.yml --tags stop
```

The above will stop the containers without destroying them, and leave the postgres and elastic data directories in place.
