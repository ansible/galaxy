.. _creating_content:

****************
Creating Content
****************

.. contents:: Topics


This topic describes how to create Ansible content that can be imported into Galaxy.


.. _creating_roles:

Roles
=====

If you're unfamiliar with the concept of an Ansible role, view :ref:`ansible_roles`.

Using the `mazer <https://github.com/ansible/mazer>`_ command line tool, you can create a role using the ``init`` command.
For example, the following will create a role directory structure called ``test-role-1`` in the current working directory:

.. code-block:: bash

    $ mazer init test-role-1

.. note::
    Roles can be created using the ``ansible-galaxy`` command that comes bundled with Ansible. The command to create a role
    is ``ansible-galaxy init``
    
    Be aware ``ansible-galaxy`` will be deprecated over time, and may not support the latest features offered by the Galaxy server.

The *test-role-1* directory will contain the following:

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

For a full explanation of all subdirectories and files listed above, and how they're used by Ansible, view the 
`Roles topic at the Ansible docs site <https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html?highlight=roles>`_

Role Metadata
-------------

When Galaxy imports a role, the import process looks for metadata found in the role's ``meta/main.yml`` file. The following shows
the default metadata file created by the ``init`` command:

.. code-block:: yaml

    galaxy_info:
      role_name: foo
      author: your name
      description: your description
      company: your company (optional)

      # If the issue tracker for your role is not on github, uncomment the
      # next line and provide a value
      # issue_tracker_url: http://example.com/issue/tracker

      # Some suggested licenses:
      # - BSD (default)
      # - MIT
      # - GPLv2
      # - GPLv3
      # - Apache
      # - CC-BY
      license: license (GPLv2, CC-BY, etc)

      min_ansible_version: 1.2

      # If this a Container Enabled role, provide the minimum Ansible Container version.
      # min_ansible_container_version:

      # Optionally specify the branch Galaxy will use when accessing the GitHub
      # repo for this role. During role install, if no tags are available,
      # Galaxy will use this branch. During import Galaxy will access files on
      # this branch. If Travis integration is configured, only notifications for this
      # branch will be accepted. Otherwise, in all cases, the repo's default branch
      # (usually master) will be used.
      #github_branch:

      #
      # platforms is a list of platforms, and each platform has a name and a list of versions.
      #
      # platforms:
      # - name: Fedora
      #   versions:
      #   - all
      #   - 25
      # - name: SomePlatform
      #   versions:
      #   - all
      #   - 1.0
      #   - 7
      #   - 99.99

      galaxy_tags: []
        # List tags for your role here, one per line. A tag is a keyword that describes
        # and categorizes the role. Users find roles by searching for tags. Be sure to
        # remove the '[]' above, if you add tags to this list.
        #
        # NOTE: A tag is limited to a single word comprised of alphanumeric characters.
        #       Maximum 20 tags per role.

    dependencies: []
      # List your role dependencies here, one per line. Be sure to remove the '[]' above,
      # if you add dependencies to this list.

The following provides guidance on setting some of the metadata values that may not be so obvious:

role_name
    Use this to override the name of the role. In the past, Galaxy would apply a regex expression to the GitHub repository name and
    automatically remove 'ansible-' and 'ansible-role-'. For example, if your repository name was 'ansible-role-apache', the role name
    would translate to 'apache'. Galaxy no longer does this automatically. Instead, use the *role_name* setting to tell Galaxy what
    the role name should be. If no value is provided, then the role name will match the repository name.

platforms
    Provide a list of valid platforms, and for each platform, a list of valid versions. The obvious question of course is, where does one
    find the list of valid platforms? You can find the `list of platforms here <https://galaxy.ansible.com/api/v1/platforms/>`_. The list
    is paginated. Click on the ``next_link`` value to get to view the next page. It's not the pretiest interface, but for now, it works.
    
    You can also search by name. For example, to search for all Ubuntu versions by adding ``?name__icontains=ubuntu`` to the query. The full
    URL will be `https://galaxy.ansible.com/api/v1/platforms/?name__icontains=ubuntu <https://galaxy.ansible.com/api/v1/platforms/?name__icontains=ubuntu>`.

galaxy_tags
    Provide a list of tags. A tag is a single world that helps categorize your role. You can invent tags, or guess at tags other might be
    using to describe similar roles, but why do that, when you can see what others are using by `browsing existing tags here <https://galaxy-qa.ansible.com/api/v1/tags/>`_.

    As with *platforms*, you can search by name here as well. For example, to see if the 'database' tag exists, add ``?name_icontains=database``
    to the query. The full URL will be `https://galaxy.ansible.com/api/v1/tags/?name__icontains=database <https://galaxy.ansible.com/api/v1/tags/?name__icontains=database>`_.

dependencies
    In a nutshell, dependencies are installed when the role is installed, and dependencies are executed before the role is executed. During role
    install and execution, dependencies are recursive, meaning dependencies can have dependencies. If a role appears more than once in the
    dependency chaing, it will only be executed one time, provided that parameters defined on the dependency are not different. 

    If the above sounds confusing, and you need more information, and an example or two, `view the Role Dependencies topic at the Ansible docs site _<https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html#role-dependencies>`.

.. _creating_multirole_repos:

Multi-role Repositories
=======================

As the name suggests, a multi-role repository can contain many roles. Traditionally, a role is a single GitHub repository. Galaxy v3.0 introduces a tech-preview
feature that enables importing a repository containing many roles.

.. note::
    This is a Tech-Preview feature. Future Galaxy releases may introduce breaking changes.

For the import to find the roles, you'll need to place them in a ``roles`` subdirectory, or provide a ``roles`` symbolic link to a directory containing
the roles. The following shows the directory structure of a multi-role repository:

.. code-block:: bash
    
    .travis.yml
    README.md
    roles/
        role-a/
        role-b/
        role-c/

There is no top-level ``meta/main.yml`` file in a multi-role repository; instead, each role within the ``roles`` subdirectory will have its own
metadata file, and for each role, follow the guide above to create it, and set the metadata values.

.. note::
    Installing roles from a multi-role repository requires using `mazer <https://github.com/ansible/mazer>`_.

To install roles from a mutli-role repository, use the new `mazer CLI tool <https://github.com/ansible/mazer>`_. For more on installing content,
view the :ref:`installing_content`. 

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
