# Contributing

## Opening Issues

The issue log is at [galaxy-issues](https://github.com/ansible/galaxy-issues). Eventually it may be merged into the Galaxy repo, but for now please continue to open issues there.

## Development

To setup a local development environment you will need to install the following:

* [Ansible Container](https://github.com/ansible/ansible-container) running from source. For assistance, see [the Running from Source guide](http://docs.ansible.com/ansible-container/installation.html#running-from-source).

* We recommend using [Git Flow](https://github.com/nvie/gitflow), although it's not strictly required. Any development 
should be done in feature branches, and compared to the `develop` branch.

### Start a Feature

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

Start developing by first creating a feature branch. The simplest way is by using Git Flow: 

```
cd ~/projects/galaxy
git flow feature start mynewfeature
```

### Build Galaxy

You should already have Docker running and Ansible Container installed. To build the Galaxy images, run the following from the root directory of your Galaxy clone:

```
$ make build
```

**NOTE**: The build process downloads images from Docker Hub for most services, excluding *django* and *gulp*. The *django* and *gulp* services are built from a *centos:7* base image, and the build involves downloading and installing both *yum* and *pip* packages. The build can run from 10 minutes up to an hour depending on the speed of your internet connection, and the amount of available CPU and memory.

After the build completes, you will see the following Docker images:

```
# View the Galaxy images
$ docker images

REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
galaxy-django       20170717173749      b7f05cefadbe        23 minutes ago      872MB
galaxy-django       latest              b7f05cefadbe        23 minutes ago      872MB
galaxy-gulp         latest              2461ebb38ac5        4 hours ago         405MB
galaxy-gulp         20170714223513      47702c4705ec        2 days ago          405MB
galaxy-conductor    latest              21f24543e888        2 days ago          518MB
memcached           latest              4b6d78556a83        10 days ago         82.6MB
centos              7                   36540f359ca3        11 days ago         193MB
rabbitmq            latest              f8fb6fc4d6ff        3 weeks ago         124MB
elasticsearch       2.4.1               8e3cf79edcc3        8 months ago        346MB
postgres            9.5.4               2417ea518abc        8 months ago        264MB
```

Start the services by running the following:

```
# Start the Galaxy services
$ make run
```

The *django* service executes the Django development web server and a celery process. Before starting the web server for the first time, it will perform database migrations, load test data, and rebuild the search indexes. These operations may take up to 10 minutes, so before attempting to access the web server, check the log file to see which task is being executed, and whether or not the web server has started. The following command will attach to the service's STDOUT and display the log output in realtime:

```
# Follow the django service log output
$ docker logs -f galaxy_django_1
```

Once the web server starts, use Ctrl-C to stop following the log output, or switch to a different terminal session. 

You can access the web server at [http://localhost:8000](http://localhost:8000).

### Create an admin user

To create a superuser with access to the admin site, open a new terminal session or window, and run `make createsuperuser`. The following shows the creation of an admin user: 

```
$ make createsuperuser
Create Superuser

Username: admin
Email address: noemail@noemail.com
Password:
Password (again):
Superuser created successfully.
```
The admin site can be accessed at [http://localhost:8000/galaxy__admin__site](http://localhost:8000/galaxy__admin__site).

### Connect to GitHub

To log into the development site, you first have to authorize it as a GitHub Oauth Application. You can do this by logging 
into GitHub, going to Personal Settings, choosing `Oauth Applications`, and then doing the following to create a new app:

- Click `Register New Application`
- Set the *Homepage URL* to `http://localhost:8000`. If you're using Docker Machine, replace *localhost* with the IP address 
of the Virtualbox host.
- Set the *Authorization Callback URL* to `http://localhost:8000/accounts/github/login/callback/`. And again, if you're using Docker Machine, replace *localhost* with the IP address of the Virtualbox host.

After you save the new application, access your local Galaxy admin site at [http://localhost:8000/galaxy__admin__site](http://localhost:8000/galaxy__admin__site). If you have not already done so, follow the *Create an Admin User* instructions above.

After logging into the admin site, you'll create a new social application. Start by finding `Social applications` at the bottom of the table, and clicking the *Add* button to its right. On the next screen, set the *provider* to `GitHub`, and enter `GitHub` as the *name*. From the new GitHub Oauth application you just created, copy the *ClientID* value into *Client id*, and copy the *Client Secret* value into *Secret key*. Under *Sites*, add `localhost` to *Chosen sites*. Save the changes.

Log out of the *admin* account, and go back to [http://localhost:8000(http://localhost:8000). Click the GitHub logo under `Log into Galaxy with GitHub`. On the next screen, you should see the message `Verify Your Email Address`.

The email was written to a log file found on the *django* container. To access it, use the following commands to connect to the container and view the file:
```
# Connect to the container and start the bash shell
$ docker exec -it ansible_django_1 /bin/bash

# Set the working directory to /galaxy_logs/email
$ cd /galaxy_logs/email

# List the log files
$ ls -l

total 4
-rw-r--r-- 1 django root 863 Jan 19 05:04 20170119-000450-139972593475792.log

# Show the contents of the latest message
$ cat 20170119-000450-139972593475792.log

From: webmaster@localhost
To: foo@gmail.com
Date: Thu, 19 Jan 2017 05:04:50 -0000
Message-ID: <20170119050450.181.62126@c164ede7ada7>

You are receiving this email because someone (hopefully you) created an account at https://galaxy.ansible.com. To confirm this is correct, please click on the following link to verify your email address:

http://localhost:8000/accounts/confirm-email/MQ:1cU4u2:SfDV-p07an0_hv5K9ggi1kuPbJM/

If you believe you have received this email in error, please disregard it.

If you have any questions regarding this email, or if you have trouble with the link provided above, please contact support.

Thanks!
```
From the latest log file, retrieve the verification URL, and paste it into your browser. Once the page loads, click the `Confirm` button, and on the next page click the blue GitHub logo to log in.

### Modifying static assets

The Javascript, CSS and HTML components for the web site can be found in the [galaxy/static](./galaxy/static) folder. The *gulp* service watches for modification to the `less` stylesheets, and automatically recompiles the CSS. After making a change, refresh your browser, and you should see the changes. If you don't see the changes, use the following command to check the gulp service's log:

```
# View the gulp service log
$ docker logs galaxy_gulp_1
```

### Stop services 

To stop all services, run `make stop`. You can then run `docker ps` to check the state of the services.

### Other useful commands

Review the Makefile for additional commands. Examples include:

- `make build_indexes` to rebuild the search indexes
- `make clean` to remove all galaxy images, containers and logging data
- `make createsuperuser` to create the Django admin user 
- `make migrate` to generate and apply Django migrations
- `make psql` to access the database command line tool 
- `make refresh` to remove all galaxy images, containers, logging data, rebuild images, and restart the containers 

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

