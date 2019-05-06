.. _creating_content_collections:

********************
Creating Collections
********************

.. contents:: Topics

This topic describes how to build a collection and distribute it through Galaxy.

.. _creating_collections:

Collections
===========

Collections are a distribution format for Ansible content. They can be used to
package and distribute roles, modules and plugin types.

.. note::
    This is a Tech-Preview feature and is only supported by Ansible 2.8 (or greater).
    Future Galaxy or Ansible releases may introduce breaking changes.


Collection Metadata
===================

Collections require a ``galaxy.yml`` at the root level of the collection. This file contains all of the metadata that Galaxy
and Mazer need in order to package and import a collection.

.. note::
    mazer will only accept ``.yml`` extensions for galaxy.yml.

::

    collection/
    ├── README.md
    ├── galaxy.yml
    ├── plugins/
    │   ├── modules/
    │   │   └── module1.py
    │   ├── inventory/
    │   └── .../
    └── roles/
        ├── role1/
        └── role2


``galaxy.yml`` requires the following fields in order to be accepted by galaxy:

.. code-block:: yaml

    namespace: "namespace_name"
    name: "collection_name"
    version: "1.0.12"
    readme: "README.md"
    authors:
        - "Author1"
        - "Author2 (http://author2.example.com)"
        - "Author3 <author3@example.com>"
    dependencies:
        - "collection.name1"
        - "collection.name2"
    description: "Example collection metadata"
    license:
        - "MIT"
    tags:
        - demo
        - collection
    repository: "https://www.github.com/my_org/my_collection"
    documentation: "http://my-docs.example.com"
    homepage: "http://www.example.com"
    issues: "https://www.github.com/my_org/my_collection/issues"


Required Fields:
    - ``namespace`` and ``name`` can only contain alphanumeric characters and underscores.
      Additionally neither can start with underscores or numbers and cannot contain consecutive
      underscores.
    - ``version`` numbers must be compatibly with semantic versioning.
    - ``readme`` contains the filename for the readme file, which can either be markdown (.md) or
      reStructuredText (.rst).


Optional Fields:
    - ``dependencies``: A list of collections that this collection depends on. Collections only
      allow other collections as dependencies, not traditional roles.
    - ``description``: A short summary description of the collection.
    - ``license``: Either a single license or a list of licenses for content inside of a collection.
      Galaxy currently only accepts `SPDX <https://spdx.org/licenses/>`_ licenses.
    - ``tags``: a list of tags. These have the same character requirements as ``namespace`` and ``name``.
    - ``repository``: URL of originating SCM repository.
    - ``documentation``: URL for online docs.
    - ``homepage``: URL for project homepage.
    - ``issues``: URL for issue tracker.


Building and Distributing
=========================

Building collections requires using the ``mazer`` command line tool available at the `Ansible
Mazer project <https://github.com/ansible/mazer>`_.

Collections are built by running ``mazer build`` from inside the collection's root directory.
This will create a ``releases`` directory inside the collection with the build artifacts,
which can be uploaded to Galaxy.

::

    collection/
    ├── ...
    ├── releases
    │   └── namespace_name-collection_name-1.0.12.tar.gz
    └── ...

    .. note::

        Changing the filename of the tarball in the release directory so that it doesn't match
        the data in ``galaxy.yml`` will cause the import to fail.


Upload Using Mazer
    Artifacts can be uploaded with Mazer using ``mazer publish --api-key=SECRET path/to/namespace_name-collection_name-1.0.12.tar.gz``

    Your API key can be found at `galaxy.ansible.com/me/preferences <https://galaxy.ansible.com/me/preferences>`_.


Upload Using Galaxy UI
    Go to the `My Content <https://galaxy.ansible.com/my-content/namespaces>`_ page and
    click the Add Content button on one of your namespaces. When the Add Content
    dialogue pops up, select Upload New Collection and select your collection from
    the files on your computer.

    When uploading collections it doesn't actually matter which namespace you select in the UI.
    The collection will get uploaded to whichever namespace is specified by the collection's
    ``galaxy.yml`` file. If you're not an owner of the namespace the upload request will
    fail.


Once a version of a collection has been uploaded it cannot be deleted or modified, so make
sure that everything looks okay before uploading them. The only way to change a collection
is to release a new version of it. The latest version of the collection (by highest version number)
will be the version that is displayed everywhere in Galaxy, but users will
also be able to download any older versions of the collection that have been uploaded.
