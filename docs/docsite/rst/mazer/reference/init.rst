.. _mazer_reference_init:

init
====

.. program::mazer init [options] role_name

Initialize a new role directory structure in the current working directory. Creates a directory for the specified *role_name*
with the default role directory structure underneath it.

The default directory structure contains the following:

.. code-block:: bash

    .travis.yml
    README.md
    defaults/
        main.yml
    files/
    handlers/
        main.yml
    meta/
        main.yml
    tasks/
        main.yml
    templates/
    tests/
        inventory
        test.yml
    vars/
        main.yml

.. option:: -i, --init-path

Path to the directory containing Galaxy content.

.. option:: --offline

Prevents Mazer from sending requests to the Galaxy server.

.. option:: --role-skeleton

Path to an existing role on which the new role should be based.

.. option:: --type

Initialize using an alternate role type. Valid type include: 'default' and 'apb'.
