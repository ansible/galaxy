
.. _creating_content_apb:

*************
Creating APBs
*************

.. contents:: Topics

This topic describes how to create an Ansible Playbook Bundle (APB)

.. _creating_apbs:

Ansible Playbook Bundles
========================

If you're unfamiliar with Ansible Playbook Bundles (APBs), view the :ref:`ansible_playbook_bundles` topic.

Using the `mazer <https://github.com/ansible/mazer>`_ command line tool, you can create an APB using the ``init`` command.
For example, the following will create a directory structure called ``test-apb-1`` in the current working directory:

.. code-block:: bash

    $ mazer init --type apb test-apb-1

.. note::
    APBs can be created using the ``ansible-galaxy`` command that comes bundled with Ansible. The command to create an APB
    is ``ansible-galaxy init --type apb``
    
    Be aware ``ansible-galaxy`` will be deprecated over time, and may not support the latest features offered by the Galaxy server.

The *test-apb-1* directory will contain the following:

.. code-block:: bash

    .travis.yml
    Dockerfile
    Makefile
    README.md
    apb.yml
    defaults/
        main.yml
    files/
    handlers/
        main.yml
    meta/
        main.yml
    playbooks/
        deprovision.yml
        provision.yml
    tasks/
        main.yml
    templates/
    tests/
        ansible.cfg
        inventory
        test.yml
    vars/
        main.yml

For more on developing and using APBs to deploy applications on OpenShift, visit the `ansibleplaybookbundle/ansible-playbook-bundle
project <https://github.com/ansibleplaybookbundle/ansible-playbook-bundle>`_.
