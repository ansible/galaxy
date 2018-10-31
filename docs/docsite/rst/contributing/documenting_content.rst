.. _documenting_content:

**************************
Documenting Galaxy content
**************************

.. contents::
   :local:

This topic describes how to document Ansible content that can be imported into Galaxy.

.. _documenting_readme:

Documenting with README.md
===========================

When you look at a role or a repository on `Galaxy <https://galaxy.ansible.com/home>`_, the first thing you see is the README page. For simple projects, this may be all the documentation you need. When you used the ``ansible-galaxy init``  or ``mazer init`` command to create the shell of your content, it placed a sample ``README.md`` file in the top-level directory of your project.

.. code-block:: bash

    .travis.yml
    README.md
    defaults/
        main.yml
        ...

This file has the following sections by default:

* Role name (with installation instructions)
* Requirements
* Role variables (if applicable)
* Dependencies (if applicable)
* License
* Author

You can add other sections, such as a Functions section to document the functions that your Galaxy content provides. See `config_manager <https://galaxy.ansible.com/ansible-network/config_manager>`_ for an example of documentation for a role.

.. _extending_documentation:

Extending documentation beyond README.md
========================================

If your Galaxy content is more complex, you may need to extend the documentation beyond a single ``README.md`` file. To extend documentation, create a ``docs/`` subdirectory in your main Galaxy content top-level directory and add individual ``.md`` files there.

See `config_manager/docs <https://github.com/ansible-network/config_manager/tree/devel/docs>`_ for an example of this.

You can then link to those files from the main ``README.md`` file:

.. code-block:: bash

    This section provides a list of the available functions that are including
    in this role.

    * get [[source]](https://github.com/ansible-network/config_manager/blob/devel/tasks/get.yaml) [[docs]](https://github.com/ansible-network/config_manager/blob/devel/docs/get.md)


You should have separate documentation for functions or embedded plugins included in your Galaxy content that documents the following:

* Introduction
* Examples
* Arguments
* Notes (if applicable)

See the `config_manager get function <https://github.com/ansible-network/config_manager/blob/devel/docs/get.md>`_ for an example of function-based documentation.
