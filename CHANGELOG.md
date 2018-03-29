## [2.4.0] - 2017-12-04

### added

-   Add AWS billing tags
    Add `Ice` billing tag to all AWS instances
-   Install sdist / wheel to docker image
-   Add "Demo" role type to Role model
-   OpenShift Installer
    - Upgrading elastic to 2.4.6. That's the highest release we can get to, due to `drf-haystack` not supporting >=5
    - Switching to an OpenShift compatible Postgresql image. Now using the same image used by AWX.
    - Modified our DEV setup to use the new images in an effort to keep things consistent, and make it easier to test and troubleshoot
    - Add OpenShift to the INSTALL.doc
    - In the effort to get tests running with the new postgres image, Implemented 12factor DATABASE_URL using dj-database-url module
-   Add post deployment cleanup tasks
-   Add django.contrib.humanize app to production settings
-   Add `userStarredApp` task to `build` step in gulpfile
-   Cloud providers implementation
-   Display cloud platforms in roles list
-   Human readable dates on display role page
-   Try fileglob in quotes
-   Display user starred repositories

### changed

-   Improve PEP8 compliance
    * E231 - Missing whitespace after ','
    
-   Adds installer
    - Tested local install 
    - Tested remote install 
    - For remote install, did as much as I could to speed copy of custom image to the remote host
    - Implemented `root_path` in `copy_branding.yml`
    - Don't think the version number matters (commit hash vs. commit count). 
    - Added INSTALLER.md and updated README.md
    
-   Updates to installer
    - Use `galaxy-manage`
    - Adds test-data directory to release and dev images
    - Remove existing, obsolete files from test-data
    - Adds platforms.json (created using galaxy-manage dumpdata) to test-data
    - Updates INSTALL doc with latest changes
-   Refactoring: Improve code quality
    * Partially fix flake8 errors: E501 - Line too long
    * Use keyword arguments in functions with multiple parameters
      for better readability
-   Update roadmap with 2.4
-   Update AUTHORS
    Move email aliases to .mailmap
-   Update Galaxy menu items and labels
-   Make model field `Stargazer.role` not nullable

### fixed

-   Fix video model
-   Fix build/static for docker and production builds
-   Fix flake8 errors
-   Move ADMIN_URL_PATTERN to default settings
    Fix default settings. Move parameter ADMIN_URL_PATTERN
    from development settings to default settings.
-   Fix handling repository got renamed when refreshing repos
    Issue #177
-   Refactoring: Fix long lines
-   Set DJANGO_SETTINGS_MODULE for galaxy-manage
    Attempting to fix overnight job that refreshes role counts
-   Deploy wheel file
    Not sure what changed, but deploying the `tar.gz` file results in the following error:
    
    ```
    pip install galaxy-2.3.1.dev78+gad2c2cb.tar.gz
    Processing ./galaxy-2.3.1.dev78+gad2c2cb.tar.gz
        Complete output from command python setup.py egg_info:
        fatal: Not a git repository (or any of the parent directories): .git
        Traceback (most recent call last):
          File "<string>", line 1, in <module>
          File "/tmp/pip-IBPjeF-build/setup.py", line 82, in <module>
            version=version.get_git_version(),
          File "galaxy/common/version.py", line 49, in get_git_version
            'git', 'describe', '--match', TAG_PREFIX + '*']
          File "/usr/lib64/python2.7/subprocess.py", line 575, in check_output
            raise CalledProcessError(retcode, cmd, output=output)
        subprocess.CalledProcessError: Command '['git', 'describe', '--match', 'v*']' returned non-zero exit status 128
    ```
    
    Using the wheel file seems to work.
-   Attempting to fix deployments
-   Fixing broken deployment bits
    - Perhaps because we're installing the wheel file, not sure, but `wsgi.py` is not ending up in the public static directory. Same with `favicon.ico`. Adding tasks to take care of these. 
    - There are a set of things that are always broken after a deployment. Adding tasks to take care of these. 
-   Add migration to fix role duplicates in database
    Migration finds all role duplicates based on `github_user` and
    `github_repo` fields and deletes them, keeping last modified one.
    Afterwards an unique constraint for these fields are created.
    
    Since Django creates all constraints as DEFERRED,
    we need to set them to IMMEDIATE to perform DDL and DML queries
    in one single transaction.
    
-   Fix migration, delete stargazers not referring to existing roles
-   Fix userStarredApp.js file name

### removed

-   Remove unique index
-   Refactoring: Remove dead code
-   Remove old wheel files
-   Remove via shell
    Remove any pre-existing wheel files using `shell`, as `with_fileglob` doesn't seem to be working.
-   Remove maintenance plugin from settings



## [2.3.1] - 2017-11-08

### unassigned

-   Release 2.3.1
    no further information available


## [2.3.0] - 2017-11-03

### added

-   Add basic unit testing suite and integrate with CI
-   Replace npm with yarn
    Replacing npm with yarn allows dramatically speedup
    nodejs dependencies installation in Docker container running on
    Linux host and therefore reduce gulp container image build time.
-   Serve static in production mode
    This change is requried to deliver a Galaxy application as a
    standalone container, which does not requre by default any
    additional web server (e.g. nginx) to serve static, so it can
    run autonomously.
-   Add `psycopg2` to requirements.txt
-   Add tools for building release container
    Add scripts that build a "build" container, which is used
    to compile static files and a "release" container.
-   Address flake8 warnings
-   Update Travis CI config according to the new dev process
-   Installer
    Building an installer modeled after the AWX installer. 
    - adds an `installer` directory
    - adds `install.yml` playbook
    - adds `inventory` file with variable for determining whether or not to perform an image build and which install path to follow
    - aims to support Docker and OpenShift
-   Enable replacing existing videos
    What's in Galaxy should reflect the current meta data for a given role. So rather than adding to the existing videos, any existing videos will be replaced.

### changed

-   Django settings fixes and improvements
-   Makefile improvements
-   Ignore W503 - an invalid flake8 warning
    W503 is an outdated warning which doesn't reflect actual PEP8[1] version
    after update[2].
    Will be replaced in future pycodestyle release[3].
    
    [1] https://www.python.org/dev/peps/pep-0008/#should-a-line-break-before-or-after-a-binary-operator
    [2] https://hg.python.org/peps/rev/3857909d7956
    [3] PyCQA/pycodestyle#498
-    Change galaxy version to 2.3.0
-   Temporary ignore flake8 E722 warning
-   Split django settings according to environment profile
-   Use a user `galaxy` to run application in release container
-   Build and publish container on merge to develop branch
-   Do not write production logs to files
-   For tmux, run commands through entrypoint.sh
-   Set DJANGO_SETTINGS_MODULE to custom for prod config
-   Build and publish release image
    Release image is automatically built and published
    when version tag is pushed to github.
-   Restore missing ui_build make target
-   Set DJANGO_SETTINGS_MODULE for task workers

### fixed

-   Fix container names in Makefile
    Update Makefile to use container names in accordance with
    ones created by ansible-container (e.g. "galaxy_django_1,
    former "ansible_django_1").
-   Temporary fix: Wait for database before running unit tests
-   Fix makefile parameter names in .travis.yml
-   Fix GALAXY_IMAGE_* variables assignment in Makefile
-   Fix tini execution from PID != 1
-   Bug fixes
    - Video import bug that caused an invalid key error
    - Provide a default elasticsearch port in production settings
    - Install gevent and use async workers. Otherwise, refreshing user role cache times out. Ran into this when testing the djgalaxy.ansible.com environment.
-   Speed up simple test
    Wait for port, rather than a fixed amount of time.
-   Fix STATICFILES_DIRS
    Trying to run deployment to QA
-   Fixes for QA/Production deployment
-   Fix ELASTICSEARCH parameter in production settings
-   Fix docker login for TravisCI scripts

### removed

-   Cleanup: Delete old scripts



## [2.2.0] - 2017-09-28

### unassigned

-   Merge missing commits master
-   Merge master into develop



## [2.1.2] - 2016-10-18

### fixed

-   Fix roles delete
-   Fix refresh when no cache entries
-   Fix tasks identifier

### changed

-   No need to update all
-   Sort versions by desc release date
-   Make volumes work when SELinux enabled
-   Only need to apply :Z once
-   Use :z when volume mounted by multiple containers
-   If repo cache exists, don't refresh, but always refresh stars on login.
-   Only pull in public repos
-   Make messages appear in celery logs
-   Using logger not print.



## [2.1.1] - 2016-10-15

### added

-   Add ability to export data
-   New test data
-   Added import and refresh_role_counts
-   Add import command
-   Add skip count to refresh

### changed

-   Refactor update role counts management task
-   Xlate role_type search param to descriptive title
-   Provide generic home page content.
-   Vertically center footer text
-   Access by token
-   Stop refreshing namespace
-   unused
-   Use unicode strings in message data.
-   Make str compare case insensitive
-   lower not lowercase
-   Migration for deleted roles
-   Remove role when GitHub namespace or name does not match
-   Update delete count

### fixed

-   Fix logging message.
-   Fix bad formatting
-   Fix delete on rename. Print output rather than log.
-   Fixes the refresh role counts task and repo cache refresh.


### unassigned
-   Bump version to 2.1.1



## [2.1.0] - 2016-10-03

### added

-   Merge latest development changes
    Styling changes for almost all interior pages including role list, role detail, adding role ratings.
-   Adding final changes

### changed

-   Provisioning Changes
    Allow for no SELinux

### fixed

-   Fixes
    A bit more styling on the intro page. Needed to adjust menu widget width based on viewport size. Attempting to automate galaxy_admin user creation after database refresh, and template the proper host name into settings.py.

### removed

-   Provisioning
    Remove .tar.gz files before copying new one.

### unassigned

-   Persist list settings to query params instead of local storage
    Sending PR to get a code review from @jimi-c before merging in. Thanks!
-   Latest Development for v1.0.0



powered by changelox
