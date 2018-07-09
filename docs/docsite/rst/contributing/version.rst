.. _versioning_content:

******************
Versioning Content
******************

.. contents:: Topics

This topic describes how to version Ansible content

.. _create_content_versions:

Creating Content Versions
=========================

Galaxy imports content from repositories on GitHub, and as part of the import process, it scans the
repository's git tags, looking for any that match the `Semantic Version <https://semver.org>`_ format.
Tags that match the format are considered to be versions and imported, and those that don't are skipped.

Once content has been pushed to a GitHub repository, it can be versioned by creating a tag using the
``git tag`` command. For more on how to create tags, view `Git Basics - Tagging <https://git-scm.com/book/en/v2/Git-Basics-Tagging>`_.

.. note::
    
    Enforcing the Semantic Version format for git tags will enable future releases of Galaxy to lock
    content versions, guaranteeing the consistency of downloaded content, and paving the way for the
    `Mazer client <https://github.com/ansible/mazer>`_ to update installed content.
