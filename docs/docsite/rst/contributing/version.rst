.. _versioning_content:

******************
Versioning Content
******************

.. contents:: Topics

This topic describes how to version Ansible content

.. _create_content_versions:

Versioning Roles
================

Galaxy imports content from repositories on GitHub, and as part of the import process, it scans the
repository's git tags, looking for any that match the `Semantic Version <https://semver.org>`_ format.
Tags that match the format are considered to be versions and imported, and those that don't are skipped.

Once content has been pushed to a GitHub repository, it can be versioned by creating a tag using the
``git tag`` command. For more on how to create tags, view `Git Basics - Tagging <https://git-scm.com/book/en/v2/Git-Basics-Tagging>`_.


Versioning Collections
======================

Version numbers are required for collections and are included in the collection's ``galaxy.yml`` file
(see :ref:`collection versions in the Ansible documentation <ansible:collection_versions>` for details).
