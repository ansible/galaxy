.. _documenting_content:

**************************
Documenting Galaxy content
**************************

.. contents:: Topics
   :local:

This topic describes how to document Ansible content that can be imported into Galaxy.

.. _documenting_readme:

Documenting with README.md
===========================

Each Galaxy content type, such as roles and multi-role repositories, includes a ``README.md`` file in the top-level directory, such as:

.. code-block:: bash

    .travis.yml
    README.md
    defaults/
        main.yml
        ...

Galaxy displays this ``README.md`` file to users when they select this content on `Galaxy <https://galaxy.ansible.com/>`_. This file should have the following sections:

* Introduction
* Requirements
* Dependencies (if applicable)
* Functions
* Examples
* License
* Author

See `config_manager <https://galaxy.ansible.com/ansible-network/config_manager>`_ for an example of documentation for a role.

You can optionally include examples within the Functions section. See :ref:`Extending documentation <extending_documentation>` for details.

.. _extending_documentation:

Extending documentation beyond README.md
========================================

Depending on the complexity of your Galaxy content, you may need to extend the documentation beyond a single ``README.md`` file. Any functions included in your Galaxy content should have separate documentation to cover the following sections per function:

* Introduction
* Examples
* Arguments
* Notes (if applicable)

To document functions or other extentions to the main ``README.md`` file, create a ``docs/`` subdirectory in your main Galaxy content top-level directory and add individual ``.md`` files there.  See `config_manager/docs <https://github.com/ansible-network/config_manager/tree/devel/docs>`_ for an example of this.

You can then link to those files from the main ``README.md`` file:

.. code-block:: bash

    This section provides a list of the available functions that are including
    in this role.

    * get [[source]](https://github.com/ansible-network/config_manager/blob/devel/tasks/get.yaml) [[docs]](https://github.com/ansible-network/config_manager/blob/devel/docs/get.md)

See the `config_manager get function <https://github.com/ansible-network/config_manager/blob/devel/docs/get.md>`_ for an example of function-based documentation.
