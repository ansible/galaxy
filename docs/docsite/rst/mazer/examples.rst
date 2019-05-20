
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


    /home/user/.ansible/collections
    └── ansible_collections
        └── testing
            └── ansible_testing_content
                ├── FILES.json
                ├── galaxy.yml
                ├── __init__.py
                ├── LICENSE
                ├── MANIFEST.json
                ├── meta
                ├── plugins
                │   ├── action
                │   │   └── add_host.py
                │   ├── filter
                │   │   ├── json_query.py
                │   │   ├── mathstuff.py
                │   │   └── newfilter.py
                │   ├── lookup
                │   │   ├── fileglob.py
                │   │   ├── k8s.py
                │   │   ├── newlookup.py
                │   │   └── openshift.py
                │   ├── modules
                │   │   ├── elasticsearch_plugin.py
                │   │   ├── kibana_plugin.py
                │   │   ├── module_in_bash.sh
                │   │   ├── mysql_db.py
                │   │   ├── mysql_replication.py
                │   │   ├── mysql_user.py
                │   │   ├── mysql_variables.py
                │   │   ├── newmodule.py
                │   │   ├── redis.py
                │   │   └── riak.py
                │   ├── module_utils
                │   │   ├── common.py
                │   │   ├── helper.py
                │   │   ├── inventory.py
                │   │   ├── lookup.py
                │   │   ├── newutil.py
                │   │   ├── raw.py
                │   │   └── scale.py
                │   └── strategy
                │       ├── debug.py
                │       ├── free.py
                │       └── linear.py
                ├── README.md
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

On the command line, use the ``--collections-path`` option to force installing content to a specific path. The following shows
the command line option in use:

.. code-block:: bash

    $ mazer install --collections-path /usr/ansible/collections geerlingguy.nginx

Viewing Installed Collections
-----------------------------

To see what's installed in the *collections_path*, use the ``list`` command. The following will list all installed
collections:

.. code-block:: bash

    $ mazer list

To list all the collections installed in a specific path, pass the ``--collections-path`` option. For example, the following
lists collections installed at ``/usr/data/ansible``:

.. code-block:: bash

    $ mazer list --collections-path /usr/data/ansible

To list the contents of a specific collection, pass the *namespace.collection_name*, as demonstrated by the following:

.. code-block:: bash

    $ mazer list testing.ansible_testing_content

Removing Installed Collections
------------------------------

Use the ``remove`` command to uninstall Ansible collections from the *collections_path*.

To remove a previously installed collection, pass *namespace.collection_name*. For example, the following demonstrates
uninstalling the collection *testing.ansible_testing_content*:

.. code-block:: bash

    $ mazer remove testing.ansible_testing_content

.. _using_mazer_content:

Using Collections in Playbooks
------------------------------


With Ansible 2.8 or higher
==========================

Collections can be referenced, found, and loaded by using a galaxy/mazer style collection name like  ``testing.ansible_testing_content``
or *namespace.collection_name*

To reference roles included in a collection in a playbook, there is a *fully qualified
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


Collection Path Details
-----------------------

Mazer installed content lives in the ansible *collections_path* ``~/.ansible/collections/``

Inside of ``~/.ansible/collections``, there is a ``ansible_collections`` directory. This
directory is the root ansible namespace for collections.

Inside of ``~/.ansible/collections/ansible_collections`` there are directories for
each galaxy namespace (typically the same name as the the github user name used in galaxy roles).
For an example of a namespace directory, the galaxy content from the
'alikins' github user will be installed to ``~/.ansible/collections/ansible_collections/alikins``

Inside each namespace directory, there will be a directory
for each ansible *collection* installed.

For new multi-content style repos (see :ref:`installing_collections`)
the *collection* level directory name will match the name of the collection
in Galaxy.

For example, for the github repo
at https://github.com/atestuseraccount/ansible-testing-content imported
to galaxy-qa at https://galaxy-qa.ansible.com/testing/ansible_testing_content, the
*collection* name and the *collection* level directory name is ``ansible_testing_content``.

Inside the *collection* level dir, there are two main directories. One
for ``roles`` and one for ``plugins``.

Inside the ``roles`` directory, each subdirectory is a *role* directory. For the ``testing`` example above,
the ``test-role-a`` *role* will be installed to ``~/.ansible/collections/ansible_galaxy/testing/ansible_testing_content/roles/test-role-a``

To use ``test-role-a`` in a playbook, it can be referenced as
``testing.ansible_testing_content.test-role-a``


