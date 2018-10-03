.. _creating_content_roles:

**************
Creating Roles
**************

.. contents:: Topics

This topic describes how to create Ansible roles that can be imported into Galaxy.

.. _creating_roles:

Roles
=====

If you're unfamiliar with the concept of an Ansible role, view :ref:`ansible_roles`.

Using the ``ansible-galaxy`` command line tool that comes bundled with Ansible, you can create a role with the ``init`` command.
For example, the following will create a role directory structure called ``test-role-1`` in the current working directory:

.. code-block:: bash

    $ ansible-galaxy init test-role-1

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
=============

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
    Optional. Use to override the name of the role.

    In the past, Galaxy would apply a regex expression to the GitHub repository name and
    automatically remove 'ansible-' and 'ansible-role-'. For example, if your repository name was 'ansible-role-apache', the role name
    would translate to 'apache'. Galaxy no longer does this automatically. Instead, use the *role_name* setting to tell Galaxy what
    the role name should be.

    If no value is provided, then the role name will match the repository name, with a couple of exceptions, including:
    converting the name to all lowercase, and replacing any '-' or '.' characters with '_'.

    .. note::

        The value of *role_name* will be converted to lowercase, and '-' and '.' will be translated to '_'.

    .. note::

        Setting the value of *role_name* on an existing role will change the name of the role by
        converting it to lowercase, and translating '-'  and '.' to '_'. If the name
        of an existing role should not be altered, don't set the value of *role_name*.

platforms
    Required. Provide a list of valid platforms, and for each platform, a list of valid versions. The obvious question of course is, where does one
    find the list of valid platforms? You can find the `list of platforms here </api/v1/platforms/>`_. The list
    is paginated. Click on the ``next_link`` value to get to view the next page. It's not the prettiest interface, but for now, it works.

    You can also search by name. For example, to search for all Ubuntu versions by adding ``?name__icontains=ubuntu`` to the query. The full
    URL will be `https://galaxy.ansible.com/api/v1/platforms/?name__icontains=ubuntu <https://galaxy.ansible.com/api/v1/platforms/?name__icontains=ubuntu>`.

galaxy_tags
    Optional. Provide a list of tags. A tag is a single word that helps categorize your role. You can invent tags, or guess at tags other might be
    using to describe similar roles, but why do that, when you can see what others are using by `browsing existing tags here <https://galaxy-qa.ansible.com/api/v1/tags/>`_.

    As with *platforms*, you can search by name here as well. For example, to see if the 'database' tag exists, add ``?name_icontains=database``
    to the query. The full URL will be `https://galaxy.ansible.com/api/v1/tags/?name__icontains=database <https://galaxy.ansible.com/api/v1/tags/?name__icontains=database>`_.

dependencies
    Optional. In a nutshell, dependencies are installed when the role is installed, and dependencies are executed before the role is executed. During role
    install and execution, dependencies are recursive, meaning dependencies can have dependencies. If a role appears more than once in the
    dependency chaining, it will only be executed one time, provided that parameters defined on the dependency are not different.

    If the above sounds confusing, and you need more information, and an example or two, `view the Role Dependencies topic at the Ansible docs site <https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html#role-dependencies>`_.

Role Names
==========

Prior to Galaxy v3.0, the role import process would alter the GitHub repository name to create the role name. Specifically, it would
apply a regular expression, and remove 'ansible-' and 'role-' from the repository name. For example, a repository name of
*ansible-role-apache* would become *apache*.

Starting in v3.0, Galaxy no longer perform this calculation. Instead, the default role name is the unaltered repository name, with a
couple minor exceptions, including: converting the name to all lowercase, and replacing any '-' or '.' characters with '_'.

To override the default name, set the ``role_name`` attribute in the role ``meta/main.yml`` file. The following snippet from a
``meta/main.yml`` file provides an example of setting the *role_name* attribute:

.. code-block:: yaml

   galaxy_info:
     role_name: apache
     description: Install the httpd service
     company: Acme, Inc.


.. note::

    Role names are limited to lowercase word characters (i.e., a-z, 0-9) and '_'. No special characters are allowed, including '.',
    '-', and space. During import, any '.' and '-' characters contained in the repository name or role_name will be replaced with '_'.

.. note::

    Setting the value of *role_name* on an existing role will change the name of the role by converting it
    to lowercase, and translating '-'  and '.' to '_'. If the name of an existing role should not be
    altered, don't set the value of *role_name*.

.. note::

    `role_name` is not used at all if the role is installed using its Git URL. Instead, the name of the repo is used.
