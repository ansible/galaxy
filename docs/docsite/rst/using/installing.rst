.. _installing_content:

******************
Installing content
******************

.. contents:: Topics

This topic describes how to download and install Ansible content from Galaxy.

.. _installing_roles:

Roles
=====

Use the ``ansible-galaxy`` command to download roles from the `Galaxy server <https://galaxy.ansible.com>`_.
For example, the following downloads the `debops.apt role <https://galaxy.ansible.com/debops/apt/>`_:

.. code-block:: bash

    $ ansible-galaxy install debops.apt

Determining Where Roles Are Installed
-------------------------------------

When Ansible is first installed, it defaults to installing content in */etc/ansible/roles*, which requires
*root* privileges.

The first way to override the default behavior is to use the *--roles-path* option on the command line, as
demonstrated by the following example:

.. code-block:: bash

    $ ansible-galaxy install --roles-path ~/ansible-roles debops.apt

Override the default behavior by setting the environment variable ``ANSIBLE_ROLES_PATH``. When set, the
*ANSIBLE_ROLES_PATH* variable is used during playbook execution to locate installed roles, and by ``ansible-galaxy``
to determine where to install roles. It can be set to a single directory path, or to a list of paths
(e.g., */etc/ansible/roles:~/.ansible/roles*). If set to a list, ``ansible-galaxy`` will install roles to
the first writable path.

Ansible also supports a `configuration file <https://docs.ansible.com/ansible/latest/installation_guide/intro_configuration.html>`_,
where ``roles_path`` can be set. Setting the value of ``roles_path`` behaves the same as setting the
*ANSIBLE_ROLES_PATH* environment variable.

Role Versions
-------------

When the Galaxy server imports a role, it imports any git tags matching the `Semantic Version format <https://semver.org/>`_ as
versions. In turn, a specific version of a role can be downloaded by specifying one of the imported tags.

To see the available versions, locate the role on the search page, and click on the name to view more details. You
can also navigate directly to the role using the */<namespace>/<role name>*. For example, to view the
role *geerlingguy.apache*, go to `https://galaxy.ansible.com/geerlingguy/apache <https://galaxy.ansible.com/geerlingguy/apache>`_.

Install a specific version of a role by appending a comma and a version tag. For example, the following installs *v1.0.0* of the
role.

.. code-block:: bash

   $ ansible-galaxy install geerlingguy.apache,v1.0.0

It's also possible to point directly to the git repository and specify a branch name or commit hash as the version.
For example, the following installs a specific commit:

.. code-block:: bash

   $ ansible-galaxy install git+https://github.com/geerlingguy/ansible-role-apache.git,0b7cd353c0250e87a26e0499e59e7fd265cc2f25

Listing Your Installed Roles
----------------------------

You can use the ``ansible-galaxy list`` command to list all the roles and role versions you have installed.

.. code-block:: bash

  $ ansible-galaxy list
   - ansible-network.network-engine, v2.7.2
   - ansible-network.config_manager, v2.6.2
   - ansible-network.cisco_nxos, v2.7.1
   - ansible-network.vyos, v2.7.3
   - ansible-network.cisco_ios, v2.7.0

Installing Multiple Roles From a File
-------------------------------------

Multiple roles can be installed by listing them in a *requirements.yml* file. The format of the file is
YAML, and the file extension must be either *.yml* or *.yaml*.

Use the following command to install roles included in *requirements.yml*:

.. code-block:: bash

    $ ansible-galaxy install -r requirements.yml

Each role in the file will have one or more of the following attributes:

   src
     The source of the role, and a required attribute. Specify a role from Galaxy by using the format
     *namespace.role_name*, or provide a URL to a repository within a git based SCM.
   scm
     If the *src* is a URL, specify the SCM. Only *git* or *hg* are supported. Defaults to *git*.
   version:
     The version of the role to download. Provide a tag value, commit hash, or branch name.
     Defaults to *master*.
   name:
     Download the role to a specific name. Defaults to the Galaxy name when downloading from Galaxy,
     or the name of the repository, when *src* is a URL.

The following example provides a guide for listing roles in a *requirements.yml* file:

.. code-block:: yaml

    # from galaxy
    - src: yatesr.timezone

    # from GitHub
    - src: https://github.com/bennojoy/nginx

    # from GitHub, overriding the name and specifying a specific tag
    - src: https://github.com/bennojoy/nginx
      version: master
      name: nginx_role

    # from a webserver, where the role is packaged in a tar.gz
    - src: https://some.webserver.example.com/files/master.tar.gz
      name: http-role

    # from Bitbucket
    - src: git+http://bitbucket.org/willthames/git-ansible-galaxy
      version: v1.4

    # from Bitbucket, alternative syntax and caveats
    - src: http://bitbucket.org/willthames/hg-ansible-galaxy
      scm: hg

    # from GitLab or other git-based scm
    - src: git+ssh://git@gitlab.company.com/mygroup/ansible-base.git
      scm: git
      version: "0.1"  # quoted, so YAML doesn't parse this as a floating-point value

Multiple Roles From Multiple Files
----------------------------------

Using the *include* directive, additional YAML files can be included into a single *requirements.yml*
file. For large projects, this provides the ability to split a large file into multiple smaller files.

For example, a project may have a *requirements.yml* file, and a *webserver.yml* file. The following
shows the contents of the *requirements.yml* file:

.. code-block:: bash

    # from galaxy
    - src: yatesr.timezone
    - include: <path_to_requirements>/webserver.yml

Below are the contents of the *webserver.yml* file:

.. code-block:: bash

    # from github
    - src: https://github.com/bennojoy/nginx

    # from Bitbucket
    - src: git+http://bitbucket.org/willthames/git-ansible-galaxy
      version: v1.4

To install all the roles from both files, pass the root file, in this case *requirements.yml* on the
command line, as demonstrated by the following:

.. code-block:: bash

    $ ansible-galaxy install -r requirements.yml

Dependencies
------------

Roles can be dependent on roles, and when a role is installed, any dependencies are automatically installed
as well.

Dependencies are listed in a role's ``meta/main.yml`` file, using the top-level *dependencies* keyword.
The following shows an example ``meta/main.yml`` file with dependent roles:

.. code-block:: yaml

    ---
    dependencies:
      - geerlingguy.java

    galaxy_info:
      author: geerlingguy
      description: Elasticsearch for Linux.
      company: "Midwestern Mac, LLC"
      license: "license (BSD, MIT)"
      min_ansible_version: 2.4
      platforms:
      - name: EL
        versions:
        - all
      - name: Debian
        versions:
        - all
      - name: Ubuntu
        versions:
        - all
      galaxy_tags:
        - web
        - system
        - monitoring
        - logging
        - lucene
        - elk
        - elasticsearch


If the source of a role is Galaxy, specify the role in the format *namespace.role_name*, as shown in the
above example. The more complex format used in *requirements.yml* is also supported, as demonstrated by
the following:

.. code-block:: yaml

    dependencies:
      - src: geerlingguy.ansible
      - src: git+https://github.com/geerlingguy/ansible-role-composer.git
        version: 775396299f2da1f519f0d8885022ca2d6ee80ee8
        name: composer

To understand how dependencies are handled during playbook execution, `view the Role Dependencies topic at
the Ansible doc site <https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html#role-dependencies>`_.

.. note::

    Galaxy expects all role dependencies to exist in Galaxy, and therefore dependencies to be specified
    using the *namespace.role_name* format.

.. _installing_multi_repos:

Collections
===========

See :ref:`Installing collections in the Ansible documentation <ansible:collections>` for detailed information about installing and using collections from Galaxy.
