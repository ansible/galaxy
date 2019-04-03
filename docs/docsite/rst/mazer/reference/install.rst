.. _mazer_reference_install:

install
=======

.. program::mazer install [options] [-r FILE | repo_name(s)[,version] | scm+repo_url[,version] | tar_file(s)]

Installs Ansible content from a content repository to the local filesystem.

.. option:: -c, --content-path

Path to the directory containing installed Galaxy content.

.. option:: -f, --force

Ignore that a role is already installed, and install it from scratch.

.. option:: -i, --ignore-errors  

When installing multiple roles, ignore any errors, and continue with the next role in the list.


.. option:: --namespace

The namespace to use when installing content. Required when installing from a git URL or archive.

.. option:: -n, --no-deps

Do NOT download and install any dependencies.

.. option:: -r ROLE_FILE, --role-file=ROLE_FILE

A file containing a YAML formatted list of roles to be installed. View :ref:installing_roles for more on this topic.
