
.. _mazer_install:

**********
Installing
**********

.. contents:: Topics


This topic provides instructions on installing Mazer CLI.

From source
-----------

The source code for mazer lives at `https://github.com/ansible/mazer <https://github.com/ansible/mazer>`_

.. code-block:: bash 

    $ git clone https://github.com/ansible/mazer.git
    $ cd mazer
    $ python setup.py install

Or, install the requirements via pip::

.. code-block:: bash

    $ pip install -r requirements.txt

Via pip (from git)
------------------

.. code-block:: bash

    pip install -v git+ssh://git@github.com/ansible/mazer.git
