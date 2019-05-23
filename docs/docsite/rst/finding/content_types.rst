.. _content_types:

*********************
Ansible Content Types
*********************

.. contents:: Topics


This topic describes the Ansible content types indexed by the Ansible Galaxy server.


.. _ansible_roles:

Ansible Roles
=============

A role enables the sharing and reuse of Ansible tasks. It contains Ansible playbook tasks, plus all the
supporting files, variables, templates, and handlers needed to run the tasks. A role is a complete unit of
automation that can be reused and shared.

In practical terms, a role is a directory structure containing all the files, variables, handlers, Jinja templates,
and tasks needed to automate a workflow. When a role is created, the default directory structure contains the following:

.. code-block:: bash

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

Using the following keywords, roles can be imported and executed in an Ansible playbook play:

  * `roles <https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html?highlight=roles#id6>`_
  * `import_role <https://docs.ansible.com/ansible/latest/modules/import_role_module.html?highlight=import_role>`_
  * `include_role <https://docs.ansible.com/ansible/latest/modules/include_role_module.html?highlight=include_role>`_

For more on using roles, view the `Roles topic at the Ansible docs site <https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html?highlight=roles>`_

.. _ansible_collections:

Ansible Collections
===================

Ansible 2.8 introduced support for a new packaging format for creating and sharing Ansible content. This new format is called a Collection, and it enables the combining of
multiple playbooks, roles, modules, and plugins into a single artifact. To learn more about the Collection package format, view :doc:`../contributing/creating_collections`.
To learn more about using Collections with Ansible, visit `the Ansible doc site <https://docs.ansibl.com>`_.

The new Mazer command-line tool can be used to create a Collection, publish a Collection to Galaxy, and download and install Collections from Galaxy to your local
filesystem. View :doc:`../mazer/index` to learn more about using Mazer to manage Collections. 


.. _ansible_playbook_bundles:

Ansible Playbook Bundles
========================

An Ansible Playbook Bundle (APB) is a lightweight application definition consisting of several named playbooks and a
metadata file. An APB defines a short lived container capable of orchestrating the deployment of applications to an
OpenShift Origin cluster running the Ansible Service Broker. The short lived container holds a copy of the APB, plus
an Ansible runtime environment, and any files required to perform the orchestration, including: playbooks, roles, and
dependencies.

For more details regarding the specification, and how to create and use APBs, visit the `ansibleplaybookbundle/apb
project <https://github.com/automationbroker/apb>`_
