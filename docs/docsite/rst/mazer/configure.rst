
.. _mazer_configure:

***********
Configuring
***********

.. contents:: Topics


This topic provides instructions on configuring Mazer CLI.

mazer.yml
---------

Configure Mazer by creating ``~/.ansible/mazer.yml``, a YAML formated file, on the local file sytem. The following shows
an example configuration file:

.. code-block:: yaml

    version: 1
    server:
      ignore_certs: false
      url: https://galaxy-qa.ansible.com
    collections_path: ~/.ansible/collections
    global_collections_path: /usr/share/ansible/collections

version
    The configuration format version. Defaults to 1.

server
    Provide Galaxy server connection information, including: url and ignore certs.

    Set the value of *url* to the Galaxy server address, and the *ignore_certs* to either *true* or *false*. When
    set to *true*, Mazer will not attempt to verify the server's TLS certificates.

collections_path
    Provide a path to a directory on the local filesytem where Ansible collections will be installed.
    Defaults to ``~/.ansible/collections``

global_collections_path
    Provide a path to a directory on the local filesytem where Ansible collections will be installed when using the '--global' cli option.
    Defaults to ``/usr/share/ansible/collections``

