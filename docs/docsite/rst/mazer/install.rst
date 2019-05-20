
.. _mazer_install:

**********
Installing
**********

.. contents:: Topics


This topic provides instructions on installing Mazer CLI.

Latest Stable Release
---------------------

The latest stable release is available on `PyPi <https://pypi.org>`_, and can be installed with ``pip``, as shown below:

.. code-block:: bash

    $ pip install mazer


Running from Source
-------------------

The source code for mazer lives at `https://github.com/ansible/mazer <https://github.com/ansible/mazer>`_, and you can
run the latest, bleeding edge code by cloning the repo, and running ``setup.py``, as shown below:

.. code-block:: bash

    $ git clone https://github.com/ansible/mazer.git
    $ cd mazer
    $ python setup.py install

You can also use ``pip`` to install directly from the GitHub repo, as shown in the following example:

.. code-block:: bash

    pip install -v git+ssh://git@github.com/ansible/mazer.git


.. _installing_the_companion_branch_of_ansible:

Installing the companion branch of ansible
------------------------------------------

FIXMEFIXME point to ansible 2.9 FIXMEFIXME
The source code for the branch of ansible that supports mazer lives at
`https://github.com/ansible/mazer <https://github.com/ansible/mazer>`_, and you can
run the latest, bleeding edge code by cloning the repo, and running ``setup.py``, as shown below:

.. code-block:: bash

    $ git clone -b mazer_role_loader https://github.com/ansible/ansible.git
    $ cd ansible
    $ python setup.py install

You can also use ``pip`` to install directly from the GitHub repo, as shown in the following example:

.. code-block:: bash

    pip install -e  git+ssh://git@github.com/ansible/ansible.git@mazer_role_loader#egg=ansible


Verifying installed version of ansible supports mazer content
=============================================================

The versions of ansible that support mazer content have a config option for setting the content path.
If the install ansible has this config option, mazer content will work.

To verify that, run the command ``ansible-config list | grep COLLECTIONS_PATHS``.
If 'COLLECTIONS_PATHS' is found the correct branch of ansible is installed.

.. code-block:: bash

    $ ansible-config list | grep COLLECTIONS_PATHS
    COLLECTIONS_PATHS:
