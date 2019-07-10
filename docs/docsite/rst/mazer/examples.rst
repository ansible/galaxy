
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

Collections are available starting with version 3.2 of the Galaxy server and version 2.8 of ansible.

To install a collection from Galaxy, pass the *namespace.collection_name* to the install command. The following
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

Installing collections in 'editable' mode for development
---------------------------------------------------------

To enable development of collections, it is possible to install a
local checkout of a collection in 'editable' mode.

Instead of copying a collection into ``~/.ansible/collections/ansible_collections``, this mode will
create a symlink from ``~/.ansible/collections/ansible_collections/my_namespace/my_colllection``
to the directory where the collection being worked on lives.

For example, if ``~/src/collections/my_new_collection`` is being worked on, to install
the collection in editable mode under the namespace 'my_namespace':

.. code-block:: bash

    $ mazer install --namespace my_namespace --editable ~/src/collections/my_new_collection

This will result in 'my_namespace.my_new_collection' being "installed".
The above command symlinks ``~/.ansible/collections/ansible_collections/my_namespace/my_new_collection`` to
``~/src/collections/my_new_collection``.

The install option ``--editable`` or the short ``-e`` can be used.

Note that ``--namespace`` option is required.

Installing collections specified in a collections lockfile
----------------------------------------------------------

Mazer supports specifying a list of collections to be installed
from a file (a 'collections lockfile').

To install collections specified in a lockfile, use the
``--collections-lock`` option of the ``install`` subcommand:

.. code-block:: bash

    $ mazer install --collections-lock collections_lockfile.yml


Setting the Collections path
----------------------------

Mazer installs collections to ``~/.ansible/collections`` by default. To override the default path, set *collections_path* in Mazer's configuration file,
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

Generate a collections lockfile based on installed collections
--------------------------------------------------------------

To create a collections lockfile representing the currently installed
collections:

.. code-block:: bash

    $ mazer list --lockfile

To create a lockfile that matches current versions exactly, add
the ``--frozen`` flag:

.. code-block:: bash

    $ mazer list --lockfile --frozen


To reproduce an existing installed collection path, redirect the 'list --lockfile'
output to a file and use that file with 'install --collections-lock':

.. code-block:: bash

    $ mazer list --lockfile  > collections_lockfile.yml
    $ mazer install --collections-path /tmp/somenewplace --collections-lock collections_lockfile.yml

Building ansible content collection artifacts
---------------------------------------------

Ansible collections can be publish to galaxy as ansible collection artifacts.
The artifacts are collection archives with the addition of
a generated MANIFEST.json providing a manifest of the content (files) in the archive
as well as additional metadata.

For example, to build the test 'hello' collection included in mazer
source code in tests/ansible_galaxy/collection_examples/hello/

.. code-block:: bash

    $ # From a source tree checkout of mazer
    $ cd tests/ansible_galaxy/collection_examples/hello/
    $ mazer build

This will build a collection artifact and save in the ``releases/``
directory.


Removing Installed Collections
------------------------------

Use the ``remove`` command to uninstall Ansible collections from the *collections_path*.

To remove a previously installed collection, pass *namespace.collection_name*. For example, the following demonstrates
uninstalling the collection *testing.ansible_testing_content*:

.. code-block:: bash

    $ mazer remove testing.ansible_testing_content

Migrating an existing traditional style role to a collection with 'mazer migrate_role'
--------------------------------------------------------------------------------------

.. code-block:: bash

    $ mazer migrate_role --role roles/some_trad_role/ --output-dir collections/roles/some_trad_role --namespace some_ns --version=1.2.3

The above command will create an ansible content collection
at ``collections/roles/some_trad_role/``


.. _using_collections_in_playbooks:

Using Collections in Playbooks
------------------------------


With Ansible 2.8 or higher
==========================

Collections can be referenced, found, and loaded by using a galaxy/mazer style collection name like  ``testing.ansible_testing_content``
or *namespace.collection_name*

To reference roles included in a collection in a playbook, there is a *fully qualified
name* and a *short name*.

The fully qualified name for the ``testing.ansible_testing_content`` role ``test_role_a``
would be ``testing.ansible_testing_content.test_role_a``. That is *namespace.collection_name.role_name*.

For example, for the collection ``testing.ansible_testing_content`` that
has a role named ``test_role_b`` in it, a playbook will need to use the *fully qualified name*
``testing.ansible_testing_content.test_role_b`` to load the role installed at
``~/.ansible/collections/ansible_collections/testing/testing_ansible_content/roles/test_role_b``

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
the ``test_role_a`` *role* will be installed to ``~/.ansible/collections/ansible_galaxy/testing/ansible_testing_content/roles/test_role_a``

To use ``test_role_a`` in a playbook, it can be referenced as
``testing.ansible_testing_content.test_role_a``


Collections lockfile format
---------------------------

The contents of collections lock file is a yaml file, containing a dictionary.

The dictionary is the same format as the 'dependencies' dict in
```galaxy.yml``.

The keys are collection labels (the namespace and the name
dot separated ala 'alikins.collection_inspect').

The values are a version spec string. For ex, `*` or "==1.0.0".

Example contents of a collections lockfile:

.. code-block::  yaml

    alikins.collection_inspect: "*"
    alikins.collection_ntp: "*"


Example contents of a collections lockfile specifying
version specs:

.. code-block:: yaml

    alikins.collection_inspect: "1.0.0"
    alikins.collection_ntp: ">0.0.1,!=0.0.2"

Example contents of a collections lockfile specifying
exact "frozen" versions:

.. code-block:: yaml

    alikins.collection_inspect: "1.0.0"
    alikins.collection_ntp: "2.3.4"


