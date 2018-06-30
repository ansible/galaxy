
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
