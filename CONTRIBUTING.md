# Contributing

To setup a local development environment you will need to do have the following 
installed locally:

* [Ansible Container 0.2.0+](https://github.com/ansible/ansible-container)
* [Ansible 2.1.1.0+](https://github.com/ansible/ansible)

We recommend using [Git Flow](https://github.com/nvie/gitflow), although it's not strictly required. Any development 
should be done in feature branches and compared to the `develop` branch.


## Checkout the Project and Start a Feature

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

## Build and Start the Galaxy Services

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

The postgres, memcache, elasticsearch, and rabbitmq services will run in the background, while django and gulp 
execute in the foreground, displaying the web server, celery and gulp logs in real time. 

Access the application from a browser using the URL: http://localhost:8000. If you are running Docker Machine, replace 
localhost with the IP address of the Virtual Box host.
 

## Connect to GitHub

To log into the development site, you first have to authorize it as a GitHub Oauth Application. You can do this by logging 
into GitHub, going to Personal Settings, choosing `Oauth Applications`, and then doing the following to create a new app:

- Click `Register New Application`
- Set the *Homepage URL* to `http://localhost:8000`. If you're using Docker Machine, replace *localhost* with the IP address 
of the Virtualbox host.
- Set the *Authorization Callback URL* to `http://localhost:8000/accounts/github/login/callback/`. And again, if you're using 
Docker Machine, replace *localhost* with the IP address of the Virtualbox host.

After you save the new application, go back to your Galaxy site, and in the browser enter the address 
`http://localhost:8000/admin`, replacing *localhost* with the IP address of the Virtualbox host, if you're using Docker 
Machine.

Log into the admin site using `admin` as the both the username and password, click on `Social Applications`, and then click 
`Add social application`. Set the *provider* to `GitHub`, and enter `GitHub` as the *name*. From the new GitHub Oauth 
application you just created, copy the *ClientID* value into *Client id*, and opy the *Client Secret* value into *Secret key*. 
Under *Sites*, add `localhost` to *Chosen sites*. Save the changes.

Log out of the *admin* account, and go back to `http://localhost:8000`. Click the GitHub logo under `Log into Galaxy with GitHub`.
You should see the message `Verify Your Email Address`.

Look in ~/.galaxy/logs/email. There should be a new file with a `.log` extension. Open it, retrieve the verification URL, and
paste it into your browser. And finally, click the `Confirm` button.

## Stop Services and Other Commands

Ctrl-C or closing the terminal session window stops the containers running in the foreground. To stop all containers 
run `make stop` from another terminal session. Use `docker ps` to check the state of the services.

Review the Makefile for additional commands. Examples include:

- `make psql` to access the database command line tool 
- `make migrate` to generate and apply Django migrations
- `make refresh` to remove all galaxy images, containers, logging data, rebuild images, and restart the containers 
- `make clean` to remove all galaxy images, containers and logging data

## Submitting Code

Code submissions are accepted via pull requests (PR), and they are always welcome! We may not accept them all, but we are 
always happy to review and discuss them with you.

Before submitting a large pull request for a new feature, we suggest opening an issue to discuss the feature prior to 
submission.

We reserve the right to reject submissions that are not a good fit for the project or not in keeping with the intended 
direction of the project. If you are unsure as to whether a feature is a good fit, take the time to open an issue.

Please observe the following when submitting a PR:

* Rebase instead of merge (http://git-scm.com/book/en/Git-Branching-Rebasing).
* Follow the Git Flow branching model and develop in a feature branch
* Limit the scope of a submission to a single feature or bug fix.
* Before embarking on a large feature, open an issue and submit the feature for review by the community



