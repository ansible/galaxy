
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

    Before installing roles with Mazer, review :ref:`using_collections_in_playbooks`. Mazer installs content different from
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
                ├── roles
                │   ├── foobar
                │   │   ├── defaults
                │   │   │   └── main.yml
                │   │   ├── handlers
                │   │   │   └── main.yml
                │   │   ├── meta
                │   │   │   └── main.yml
                │   │   ├── README.md
                │   │   ├── tasks
                │   │   │   └── main.yml
                │   │   ├── tests
                │   │   │   ├── inventory
                │   │   │   └── test.yml
                │   │   └── vars
                │   │       └── main.yml
                │   ├── test_role_1
                │   │   ├── defaults
                │   │   │   └── main.yml
                │   │   ├── handlers
                │   │   │   └── main.yml
                │   │   ├── meta
                │   │   │   └── main.yml
                │   │   ├── README.md
                │   │   ├── tasks
                │   │   │   └── main.yml
                │   │   ├── tests
                │   │   │   ├── inventory
                │   │   │   └── test.yml
                │   │   └── vars
                │   │       └── main.yml
                │   ├── test_role_a
                │   │   ├── defaults
                │   │   │   └── main.yml
                │   │   ├── handlers
                │   │   │   └── main.yml
                │   │   ├── meta
                │   │   │   └── main.yml
                │   │   ├── tasks
                │   │   │   └── main.yml
                │   │   ├── tests
                │   │   │   ├── inventory
                │   │   │   └── test.yml
                │   │   └── vars
                │   │       └── main.yml
                │   ├── testrolea
                │   │   ├── defaults
                │   │   │   └── main.yml
                │   │   ├── handlers
                │   │   │   └── main.yml
                │   │   ├── meta
                │   │   │   └── main.yml
                │   │   ├── tasks
                │   │   │   └── main.yml
                │   │   ├── tests
                │   │   │   ├── inventory
                │   │   │   └── test.yml
                │   │   └── vars
                │   │       └── main.yml
                │   ├── test_role_b
                │   │   ├── defaults
                │   │   │   └── main.yml
                │   │   ├── handlers
                │   │   │   └── main.yml
                │   │   ├── meta
                │   │   │   └── main.yml
                │   │   ├── README.md
                │   │   ├── tasks
                │   │   │   └── main.yml
                │   │   ├── tests
                │   │   │   ├── inventory
                │   │   │   └── test.yml
                │   │   └── vars
                │   │       └── main.yml
                │   ├── test_role_c
                │   │   ├── defaults
                │   │   │   └── main.yml
                │   │   ├── handlers
                │   │   │   └── main.yml
                │   │   ├── meta
                │   │   │   └── main.yml
                │   │   ├── README.md
                │   │   ├── tasks
                │   │   │   └── main.yml
                │   │   ├── tests
                │   │   │   ├── inventory
                │   │   │   └── test.yml
                │   │   └── vars
                │   │       └── main.yml
                │   └── test_role_d
                │       ├── defaults
                │       │   └── main.yml
                │       ├── handlers
                │       │   └── main.yml
                │       ├── meta
                │       │   └── main.yml
                │       ├── README.md
                │       ├── tasks
                │       │   └── main.yml
                │       ├── tests
                │       │   ├── inventory
                │       │   └── test.yml
                │       └── vars
                │           └── main.yml
                └── tests
                    ├── inventory
                    └── test.yml


Setting the Collections path
----------------------------

Mazer installs collections to ``~/.ansible/collections``. To override the default path, set *collections_path* in Mazer's configuration file,
``~/.ansible/mazer.yml``. The following shows an example configuration file that sets the value of *collections_path*:

.. code-block:: yaml

    version: '1.0'
    collections_path: /usr/ansible/collections

On the command line, use the ``--collections-path`` option to force installing collections to a specific path. The following shows
the command line option in use:

.. code-block:: bash

    $ mazer install --collections-path /usr/ansible/collections testing.ansible_testing_content

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

.. _using_collections_in_playbooks:

Using Collections in Playbooks
------------------------------


With Ansible 2.8 or higher
==========================

Collections can be referenced, found, and loaded by using a galaxy/mazer style collection name like  ``testing.ansible_testing_content``
or *namespace.collection_name*

To reference roles included in a collection in a playbook, there is a *fully qualified
name* and a *short name*.

The fully qualified name for the ``testing.ansible_testing_content`` role ``test-role-a``
would be ``testing.ansible_testing_content.test-role-a``. That is *namespace.collection_name.role_name*.

FIXME FIXME verify this FIXME

For example, ``mynamespace.myrole`` will match the role with the *fully qualified name*
``mynamespace.myrole.myrole`` and find it at ``~/.ansible/collections/ansible_collections/mynamespace/myrole/roles/myrole``

FIXME FIXME

For example, for the collection ``testing.ansible_testing_content`` that
has a role named ``test-role-b`` in it, a playbook will need to use the *fully qualified name*
``testing.ansible_testing_content.test-role-b`` to load the role installed at
``~/.ansible/collections/ansible_collections/testing/testing_ansible_content/roles/test-role-b``

An example playbook:

.. code-block:: yaml

    ---
    - name: Use a role from a collection
      hosts: localhost
      gather_facts: false
      roles:
        # A role from a collection using fully qualified name.
        # This is the recomended way to reference roles from collections
        - testing.ansible_testing_content.test_role_a

    - name: Use a role via include_role from a collection
      hosts: localhost
      gather_facts: false
      tasks:
        - name: Use 'test_role_b'
          include_role:
            name: testing.ansible_testing_content.test_role_b

    - name: Use a module from a collection
      hosts: localhost
      gather_facts: false
      tasks:
        - name: Use 'newmodule' from a collection
          testing.ansible_testing_content.newmodule:
          register: newmodule_results

        - name: Show 'newmodule' results
          debug:
            var: newmodule_results

    - name: Use a module from a collection with a collections path list set and 'short' name
      hosts: localhost
      gather_facts: false
      collections:
        - testing.ansible_testing_content
      tasks:
        - name: Use 'newmodule' from a collection with 'short' name
          newmodule:
          register: newmodule_results

        - name: Show 'newmodule' results
          debug:
            var: newmodule_results


Collection Path Details
-----------------------

Mazer installed collections live in the ansible *collections_path* ``~/.ansible/collections/``

Inside of ``~/.ansible/collections``, there is a ``ansible_collections`` directory. This
directory is the root ansible namespace for collections.

Inside of ``~/.ansible/collections/ansible_collections`` there are directories for
each galaxy namespace (typically the same name as the the github user name used in galaxy roles).
For an example of a namespace directory, the galaxy collection from the
'alikins' github user will be installed to ``~/.ansible/collections/ansible_collections/alikins``

Inside each namespace directory, there will be a directory
for each ansible *collection* installed.

For collections (see :ref:`installing_collections`)
the *collection* level directory name will match the name of the collection
in Galaxy. This name is set in ``galaxy.yml`` field ``name``, as descibed
in :ref:`collection_metadata`.

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


