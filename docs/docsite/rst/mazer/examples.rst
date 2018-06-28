
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

Installing Multi-role Repositories
----------------------------------

Starting with version 3.0 of the Galaxy server, many roles can be combined into a single git repository. Prior to this role repositories
were structured to only contain a single role. Mazer is able extract all of the roles from the repostory, and install them to the
local file system.

To install a multi-role repository fromn Galaxy, pass the *namespace.repository_name* to the install command. The following
installs the `testing.ansible-testing-content repository <https://galaxy.ansible.com/testing/ansible-testing-content>`_ from
Galaxy:

.. code-block:: bash

    $ mazer install testing.ansible-testing-content

.. note::
    
    Before installing roles with Mazer, review :ref:`using_mazer_content`. Mazer installs content different from
    the way ``ansible-galaxy`` does.

This will install all of the roles to ``~/.ansible/content/testing.ansible-testing-content/roles/``. The following shows
the complete directory tree created on the local file system by Mazer:

.. code-block:: bash

    $ tree ~/.ansible/content/
        /home/user/.ansible/content/
        └── testing.ansible-testing-content
            └── roles
                ├── ansible-role-foobar
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── README.md
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                ├── ansible-test-role-1
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── README.md
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                ├── test-role-a
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                ├── test-role-b
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── README.md
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                ├── test-role-c
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── README.md
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml
                └── test-role-d
                    ├── defaults
                    │   └── main.yml
                    ├── handlers
                    │   └── main.yml
                    ├── meta
                    │   └── main.yml
                    ├── README.md
                    ├── tasks
                    │   └── main.yml
                    ├── tests
                    │   ├── inventory
                    │   └── test.yml
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
        └── geerlingguy.apache
            └── roles
                ├── apache
                │   ├── defaults
                │   │   └── main.yml
                │   ├── handlers
                │   │   └── main.yml
                │   ├── meta
                │   │   └── main.yml
                │   ├── README.md
                │   ├── tasks
                │   │   └── main.yml
                │   ├── tests
                │   │   ├── inventory
                │   │   └── test.yml
                │   └── vars
                │       └── main.yml

In the above example, the actual role *apache* is located in the path ``~/.ansible/content/geerlingguy.apache/roles``. To reference
the role in a playbook, *ANSIBLE_ROLES_PATH* must include this path, and the playbook must use *apache* as the role name.

It's possible to use roles installed by Mazer, but obviously, having to update *ANSIBLE_ROLES_PATH* for each role, and change
the role name in existing playbooks is less than ideal. In the near future, the role loader in Ansible core will be modified to
support the way Mazer works.

Stay tuned for updates.
