
.. _mazer_examples:

********
Examples
********

.. contents:: Topics


This topic provides examples for using Mazer CLI.

.. _installing_collections:

Installing Collections
----------------------

Collections are a new way to package and distribute ansible related content.
See :ref:`creating_collections` for examples.

Collections are available starting with version 3.2 of the Galaxy server and version 2.9 of ansible.

To install a collection from Galaxy, pass the *namespace.repository_name* to the install command. The following
installs the `testing.ansible_testing_content collection <https://galaxy.ansible.com/testing/ansible-testing-content>`_ from
Galaxy:

.. code-block:: bash

    $ mazer install testing.ansible_testing_content

.. note::

    Before installing roles with Mazer, review :ref:`using_mazer_content`. Mazer installs content different from
    the way ``ansible-galaxy`` does.

This will install the collection to ``~/.ansible/collections/ansible_collections/testing/ansible_testing_content/``. The following shows
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

Setting the Collections path
----------------------------

Mazer installs content to ``~/.ansible/collections``. To override the default path, set *collections_path* in Mazer's configuration file,
``~/.ansible/mazer.yml``. The following shows an example configuration file that sets the value of *collections_path*:

.. code-block:: yaml

    version: '1.0'
    collections_path: /usr/ansible/collections
    options:
        verbosity: 0

On the command line, use the ``--content-path`` option to force installing content to a specific path. The following shows
the command line option in use:

.. code-block:: bash

    $ mazer install --content-path /usr/ansible/collections geerlingguy.nginx

Viewing Installed Content
-------------------------

To see what's installed in the *collections_path*, use the ``list`` command. The following will list all installed
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

Use the ``remove`` command to uninstall Ansible content from the *collections_path*.

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

In the above example, the actual role *apache* is located inside the directory ``~/.ansible/collections/geerlingguy/apache/roles`` in the ``apache`` subdir.


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


Content Path Details
--------------------

Mazer installed content lives in the ansible *collections_path* ``~/.ansible/content/``

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




