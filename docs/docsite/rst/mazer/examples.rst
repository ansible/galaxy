
.. _mazer_examples:

********
Examples
********

.. contents:: Topics


This topic provides examples for using Mazer CLI.

Installing Roles
----------------

To install a role found on `Galaxy <https://galaxy.ansible.com>`_, pass the *namespace.role_name*. For example,
the following install the role `geerlingguy.nginx <https://galaxy.ansible.com/geerlingguy/nginx/>`_ from the
Galaxy server:

.. code-block:: bash

    $ mazer install geerlingguy.nginx

.. note::

    Before installing roles with Mazer, review :ref:`using_mazer_content`. Mazer installs content different from
    the way ``ansible-galaxy`` does.

To install a specific version of the Galaxy role, append `,<semantic version>` to the name, as demonstrated by the
following:

.. code-block:: bash

    $ mazer install geerlingguy.nginx,2.6.0

Roles can also be installed directly from GitHub, by passing the git URL of the repository, and a namespace value. Use
the required *--namespace* option to provide the namespace. The following installs the same role, but bypasses the Galaxy server,
and goes directly to GitHub.

.. code-block:: bash

    $ mazer install --namespace geerlingguy git+https://github.com/geerlingguy/ansible-role-nginx

A version number can also be passed using the same ',' separated format. For example:

.. code-block:: bash

    $ mazer install git+https://github.com/geerlingguy/ansible-role-nginx,2.6.0


.. _installing_repositories_with_multiple_roles:

Installing Repositories With Multiple Roles
-------------------------------------------

Starting with version 3.0 of the Galaxy server, many roles can be combined into a single git repository. Prior to this role repositories
were structured to only contain a single role. Mazer is able extract all of the roles from the repostory, and install them to the
local file system.

To install a multi-role repository from Galaxy, pass the *namespace.repository_name* to the install command. The following
installs the `testing.ansible-testing-content repository <https://galaxy.ansible.com/testing/ansible-testing-content>`_ from
Galaxy:

.. code-block:: bash

    $ mazer install testing.ansible-testing-content

.. note::

    Before installing roles with Mazer, review :ref:`using_mazer_content`. Mazer installs content different from
    the way ``ansible-galaxy`` does.

This will install all of the roles to ``~/.ansible/content/testing/ansible-testing-content/roles/``. The following shows
the complete directory tree created on the local file system by Mazer:

.. code-block:: bash

    $ tree ~/.ansible/content/
    /home/user/.ansible/content/
    └── testing
        └── ansible_testing_content
            └── roles
                ├── ansible-role-foobar
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── README.md
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                ├── ansible-test-role-1
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── README.md
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                ├── test-role-a
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                ├── test-role-b
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── README.md
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                ├── test-role-c
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── README.md
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                └── test-role-d
                    ├── defaults
                    │   └── main.yml
                    ├── handlers
                    │   └── main.yml
                    ├── meta
                    │   └── main.yml
                    ├── README.md
                    ├── tasks
                    │   └── main.yml
                    ├── tests
                    │   ├── inventory
                    │   └── test.yml
                    └── vars
                        └── main.yml

Setting the Content path
------------------------

Mazer installs content to ``~/.ansible/content``. To override the deault path, set *content_path* in Mazer's configuration file,
``~/.ansible/mazer.yml``. The following shows an example configuration file that sets the value of *content_path*:

.. code-block:: yaml

    version: '1.0'
    content_path: /usr/ansible/content
    options:
        verbosity: 0

On the command line, use the ``--content-path`` option to force installing content to a specific path. The following shows
the command line option in use:

.. code-block:: bash

    $ mazer install --content-path /usr/ansible/content geerlingguy.nginx

Viewing Installed Content
-------------------------

To see what's installed in the *content_path*, use the ``list`` command. The following will list all installed
content:

.. code-block:: bash

    $ mazer list

To list all the content installed in a specific path, pass the ``--content-path`` option. For example, the following
lists content installed at ``/usr/data/ansible``:

.. code-block:: bash

    $ mazer list --content-path /usr/data/ansible

To list the contents of a specific repository, pass the *namespace.repository_name*, as demonstrated by the following:

.. code-block:: bash

    $ mazer list testing.ansible-testing-content

Removing Installed Content
--------------------------

Use the ``remove`` command to uninstall Ansible content from the *content_path*.

To remove a previously installed role, pass *namespace.role_name*. For example, the following demonstrates
uninstalling the role *geerlingguy.apache*:

.. code-block:: bash

    $ mazer remove geerlingguy.apache

To remove all the content intalled from a multi-role repository, pass *namespace.repository_name*, as demonstrated
by the following:

.. code-block:: bash

    $ mazer remove testing.ansible-testing-content

.. _using_mazer_content:

Using Content in Playbooks
--------------------------

Mazer places roles on the filesystem differently from the way ``ansible-galaxy`` does. For example, installing the
role *geerlingguy.apache* with Mazer creates the following directory structure:

.. code-block:: bash

    $ tree ~/.ansible/content/
        /home/user/.ansible/content/
        ├── geerlingguy
        │   └── apache
        │       └── roles
        │           └── apache
        │               ├── defaults
        │               │   └── main.yml
        │               ├── handlers
        │               │   └── main.yml
        │               ├── LICENSE
        │               ├── meta
        │               │   └── main.yml
        │               ├── README.md
        │               ├── tasks
        │               │   ├── configure-Debian.yml
        │               │   ├── configure-RedHat.yml
        │               │   ├── configure-Solaris.yml
        │               │   ├── configure-Suse.yml
        │               │   ├── main.yml
        │               │   ├── setup-Debian.yml
        │               │   ├── setup-RedHat.yml
        │               │   ├── setup-Solaris.yml
        │               │   └── setup-Suse.yml
        │               ├── templates
        │               │   └── vhosts.conf.j2
        │               ├── tests
        │               │   ├── README.md
        │               │   └── test.yml
        │               └── vars
        │                   ├── AmazonLinux.yml
        │                   ├── apache-22.yml
        │                   ├── apache-24.yml
        │                   ├── Debian.yml
        │                   ├── RedHat.yml
        │                   ├── Solaris.yml
        │                   └── Suse.yml

In the above example, the actual role *apache* is located inside the directory ``~/.ansible/content/geerlingguy/apache/roles`` in the ``apache`` subdir.


With The Companion Ansible Branch
=================================

If the `companion branch of ansible <https://github.com/ansible/ansible/tree/mazer_role_loader>`__ is installed
roles can be referenced, found, and loaded by using a galaxy/mazer style role name like  ``geerlingguy.nginx.nginx``
or *namespace.repository_name.role_name*

To reference that role in a playbook, there is a *fully qualified
name* and a *short name*.

The fully qualified name for the ``geerlingguy.apache`` role
would be ``geerlingguy.apache.apache``. That is *namespace.repository_name.role_name*.

With traditional style roles, the short name ``geerlingguy.apache`` can also be used.
Note that this name format is compatible with using roles installed with ``ansible-galaxy``.

For example, ``mynamespace.myrole`` will match the role with the *fully qualified name*
``mynamespace.myrole.myrole`` and find it at ``~/.ansible/content/mynamespace/myrole/roles/myrole``

Traditional style roles can be referenced by the *short name* or the *fully qualified name*.

For example, ``geerlingguy.apache`` will refer to the role installed at
``~/.ansible/content/geerlingguy/apache/roles/apache`` as well as the
more specific name ``geerlingguy.apache.apache``.

For a galaxy *repository* that has multiple roles, the *fully qualified name*
needs to be used since the repository name is different from the role name.

For example, for the multiple role repository ``testing.some_multi_content_repo`` that
has a role named ``some_role`` in it, a playbook will need to use the *fully qualified name*
``testing.some_multi_content_repo.some_role`` to load the role installed at
``~/.ansible/content/testing/some_multi_content_repo/roles/some_role``

An example playbook:

.. code-block:: yaml


    ---
    - name: The first play
      hosts: localhost
      roles:
        # This will load from ~/.ansible/content
        # Traditional role referenced with the style namespace.reponame.rolename style
        - GROG.debug-variable.debug-variable

        # a traditional role referenced via the traditional name
        # (namespace.reponame)
        - f500.dumpall

        # traditional role specified as dict with role vars
        - {role: GROG.debug-variable.debug-variable, debug_variable_dump_location: '/tmp/ansible-GROG-dict-style-debug.dump', dir: '/opt/b', app_port: 5001}

        - role: f500.dumpall
          tags:
            - debug
          dumpall_host_destination: '/tmp/ansible-f500-dumpall/'

        # traditional role in ~/.ansible/roles
        - some_role_from_tidle_dot_ansible

        # traditional role that is install "everywhere"
        # including ~/.ansible/content/alikins/everywhere/roles/everywhere
        #           ~/.ansible/roles/everywhere
        #           ./roles/everywhere.
        # Will find it in playbook local roles/everywhere
        - everywhere

        # traditional role (everywhere) but using namespace.repo.rolename dotted name
        # will find in ~/.ansible/content
        - alikins.everywhere.everywhere

        # traditional role (everywhere) but using gal trad style namespace.repo dotted name
        # will find in ~/.ansible/content
        - alikins.everywhere

        # A role from a multi-content repo
        - testing.ansible_testing_content.test-role-a


With Ansible Versions That Do Not Support Content Path
======================================================

Ansible releases ``2.7`` and earlier do not support the mazer *content path*.
If you are using one of these versions, there are two ways mazer installed
roles can be used.


Adding Each Role On Content Path To Roles Path
______________________________________________

To reference a role installed in the content path (``geerlingguy.apache for example``) in a playbook, *ANSIBLE_ROLES_PATH* must include
the path to the *repository* role directory (``~/.ansible/content/geerlingguy/apache/roles``), and the playbook must use ``apache`` as the role name.

It's possible to use roles installed by Mazer, but obviously, having to update *ANSIBLE_ROLES_PATH* for each role, and change
the role name in existing playbooks is less than ideal. In the mean time, the
`'mazer_role_loader' branch of ansible <https://github.com/ansible/ansible/tree/mazer_role_loader>`__ is available to try.

Stay tuned for updates.


Using Content Path Relative Paths To Roles
__________________________________________


For versions of ansible that do not support mazer content paths, there is another
option: adding ``~/.ansible/content`` to *ANSIBLE_ROLES_PATH* and using relative paths to reference roles.

In a playbook, ansible supports using the path to the role directory in addition to using the symbolic role
name. For example, a role referenced like ``apps/apache`` will look for a ``app`` sub dir in ansible role paths and
for a role dir name ``apache`` in that subdir.

Since mazer installed roles live in subdirectories of ``~/.ansible/content``, then ``~/.ansible/content`` can
be added to *ANSIBLE_ROLES_PATH*. Then a playbook can reference ``geerlingguy/apache/roles/apache`` to load
the ``geerlingguy.apache`` role installed with mazer.

To use the ``test-role-a`` role from the ``testing.ansible_testing_content`` *repository*, that
role could be referenced as ``testing/ansible_testing_content/roles/test-role-a`` which would use the
role installed to ``~/.ansible/content/testing/ansible_testing_content/roles/test-role-a``.

For an example of a ansible config file to set this up:

.. code-block:: ini

    [defaults]
    roles_path = $HOME/.ansible/content:$HOME/deploy/roles

And an example playbook:

.. code-block:: yaml

    ---
    - name: The first play
      hosts: localhost
      roles:
        - geerlingguy/apache/roles/apache
        - testing/ansible_testing_content/roles/test-role-a
      tasks:
        - name: import the role called testing.ansible_testing_content.test-role-a
          include_role:
            name: testing/ansible_testing_content/roles/test-role-a

.. note::

    When using relative (or full) paths as role names in ansible-playbook, all potential roles paths
    will be search. This include default role paths (``/etc/ansible/roles`` for example) and playbook local
    ``roles/`` directories. If there are multiple paths that match the role name used in the playbook, it
    is possible the wrong role will be used.

    To minimize this possibility it is recommended to add ``~/.ansible/content`` to the front of
    *ANSIBLE_ROLES_PATH* so ``~/.ansible/content`` relative paths will be searched first.


Content Path Details
--------------------

Mazer installed content lives in the ansible *content_path* ``~/.ansible/content/``

Inside of ``~/.ansible/content``, there are directories for
each galaxy namespace (typically the same name as the the github user name used in galaxy roles).
For an example of a namespace directory, the galaxy content from the
'alikins' github user will be installed to ``~/.ansible/content/alikins``

Inside each namespace directory, there will be a directory
for each galaxy *repository* installed. For a traditional galaxy
role, this *repository* dir will have a name that matches the role
name. See :ref:`installing_roles` for examples.

For new multi-content style repos (see :ref:`installing_repositories_with_multiple_roles`)
the *repository* level directory name with match the name of the git repo
imported to galaxy. For example, for the github repo
at https://github.com/atestuseraccount/ansible-testing-content imported
to galaxy-qa at https://galaxy-qa.ansible.com/testing/ansible_testing_content, the
*repository* level directory name is ``ansible_testing_content``.

Inside the *repository* level dir, there are directories for each *content
type* supported by galaxy. For example, ``roles``.

Inside each *content type* directory, there will be a directory named for the
each *content* of that *content type*. For the ``testing`` example above,
the ``test-role-a`` *role* will be installed to ``~/.ansible/content/testing/ansible_testing_content/roles/test-role-a``

To use ``test-role-a`` in a playbook, it can be referenced as
``testing.ansible_testing_content.test-role-a``

For a traditional role (a *role* where the upstream git repo contains only
a single role) like `geerlingguy.apache`, mazer will install it
to ``~/.ansible/content/geerlingguy/apache/roles/apache``




