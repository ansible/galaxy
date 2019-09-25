
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

Using the ``ansible-galaxy`` command that comes bundled with Ansible, you can create an APB using the ``init`` command.
For example, the following will create a directory structure called ``test-apb-1`` in the current working directory:

.. code-block:: bash

    $ ansible-galaxy init --type apb test-apb-1

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

APB Names
==========

By default Galaxy sets APB name to the unaltered repository name, with a couple minor exceptions, including: converting the name to all
lowercase, and replacing any '-' or '.' characters with '_'.

To override the default name, set the *name* attribute in the ``apb.yml`` metadata file. The following snipet from an
``apb.yml`` file provides an example of setting the *name* attribute:

.. code-block:: yaml

   version: 1.0
   name: virtualization
   description: KubeVirt installer
   bindable: False
   async: optional
   metadata:
     displayName: Kubevirt
     longDescription: |
       KubeVirt enables the migration of existing virtualized workloads directly into the development workflows supported by Kubernetes.
       This provides a path to more rapid application modernization by:
         - Supporting development of new microservice applications in containers that interact with existing virtualized applications.
         - Combining existing virtualized workloads with new container workloads on the same platform, thereby making it easier to decompose monolithic virtualized workloads into containers over time.
     documentationUrl: https://github.com/kubevirt/kubevirt/blob/master/README.md
     imageUrl: https://cdn.pbrd.co/images/H5Gutd7.png
     providerDisplayName: "Red Hat, Inc."

Since the *name* attribute is set to 'virtualization' in the above example, Galaxy will import the APB with the name
'virtualization', rather than the repository name.

.. note::

    Content names are limited to lowercase word characters (i.e., a-z, 0-9) and '_'. No special characters are allowed, including '.',
    '-', and space. During import, any '.' and '-' characters contained in the repository name or metadata *name* value  will be replaced
    with '_'.
