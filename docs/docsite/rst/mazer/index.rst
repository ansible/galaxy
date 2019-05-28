
.. _mazer:

*****
Mazer
*****

Mazer is a new command-line tool for managing `Ansible <https://github.com/ansible/ansible>`_ content, and an open source project
on GitHub at `ansible/mazer <https://github.com/ansible/mazer>`_.

.. note::

    Mazer is experimental, and currently only available for tech-preview. Use with lots of caution! It is not intended for use in
    production environments, nor is it currently intended to replace the `ansible-galaxy` command-line tool.

    If you're installing Ansible content in a production environment, or need assistance with Ansible, please visit the `Ansible Project <https://github.com/ansible/ansible>`__,
    or the `Ansible docs site <https://docs.ansible.com>`_.

.. note::

    Before installing collections with Mazer, review :ref:`using_collections_in_playbooks`. Mazer installs content differently from
    the way ``ansible-galaxy`` does.

    Mazer is most useful when used with a version of Ansible that understands *collections*.
    That means Ansible versions 2.8 or higher.

.. toctree::
   :maxdepth: 2

   install
   configure
   examples
   reference/index.rst
