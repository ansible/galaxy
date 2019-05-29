.. _mazer_reference_install:

install
=======

.. program::mazer install [options] [-r FILE | repo_name(s)[,version] | scm+repo_url[,version] | tar_file(s)]

Installs Ansible content from Galaxy to the local filesystem.

.. option:: -c, --collections-path

Path to the directory containing installed Galaxy content.
The default is ~/.ansible/collections

.. option:: -l, --lockfile

Path to a collections lockfile listing collections to install.

.. option:: -e, --editable

Link a local directory into the content path for development and testing.

.. option:: -g, --global

Install content to the path containing your global or system-wide content.

.. option:: -f, --force

Ignore that a role is already installed, and install it from scratch.

.. option:: -i, --ignore-errors

When installing multiple roles, ignore any errors, and continue with the next role in the list.

.. option:: --namespace

The namespace to use when installing content. Required when installing from a git URL or archive.

.. option:: -n, --no-deps

Do NOT download and install any dependencies.
