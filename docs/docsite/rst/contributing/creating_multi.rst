.. _creating_content_multi:

*************************
Creating Multi-role Repos
*************************

.. contents:: Topics

This topic describes how to create a mult-role repository that can be imported into Galaxy.

.. _creating_multi_roles:

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
