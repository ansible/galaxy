
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
    content_path: ~/.ansible/content
    options:
        local_tmp: ~/.ansible/tmp
        role_skeleton_ignore:
            - ^.git$
            - ^.*/.git_keep$
        role_skeleton_path: null
        verbosity: 0

version
    The configuration format version. Defaults to 1.

server
    Provide Galaxy server connection information, including: url and ignore certs.

    Set the value of *url* to the Galaxy server address, and the *ignore_certs* to either *true* or *false*. When
    set to *true*, Mazer will not attempt to verify the server's TLS certificates.

content_path
    Provide a path to a directory on the local filesytem where Ansible content will be installed.
    Defaults to ``~/.ansible/content``

options
    Miscellaneous configuration options are set here, inlcuding: local_tmp, role_skeleton, role_skeleton_path,
    verbosity. 

    *local_tmp* - path that Mazer can use for temporary work space, for doing things like expanding archive files.

    *role_skeleton_path* - path to a role structure to use with the ``init`` command. Overrides the default role
    structure.
   
    *role_skeleton_ignore* - List of file name patterns to ignore when copying the role skeleton path contents.

    *verbosity* - controls the default level of output returned by Mazer.
