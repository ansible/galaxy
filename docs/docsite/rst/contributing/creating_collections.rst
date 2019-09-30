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
package and distribute playbooks, roles, modules, and plugins.

.. note::
    This is a Tech-Preview feature and is only supported by Ansible 2.8 (or greater).
    Future Galaxy or Ansible releases may introduce breaking changes.


.. _collection_metadata:

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
        "other_namespace.collection1": ">=1.0.0"
        "other_namespace.collection2": ">=2.0.0,<3.0.0"
        "anderson55.my_collection": "*"    # note: "*" selects the highest version available
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
    - ``namespace``: the galaxy namespace that the collection will get uploaded to.
        May only contain alphanumeric characters and underscores. Additionally
        namespaces cannot start with underscores or numbers and cannot contain consecutive
        underscores.
    - ``name``: the collection's name. Has the same character restrictions as ``namespace``.
    - ``version``: the collection's version. Must be compatible with semantic versioning.
    - ``readme``: contains the filename for the readme file, which can either be markdown (.md) or
      reStructuredText (.rst).


Optional Fields:
    - ``dependencies``: A dictionary where keys are collections, and values are version
      range `specifiers <https://python-semanticversion.readthedocs.io/en/latest/#requirement-specification>`_,
      it is good practice to depend on a version range to minimize conflicts, and pin to a
      major version to protect against breaking changes, ex: ``"user1.collection1": ">=1.2.2,<2.0.0"``
      allow other collections as dependencies, not traditional roles.
    - ``description``: A short summary description of the collection.
    - ``license``: Either a single license or a list of licenses for content inside of a collection.
      Galaxy currently only accepts `SPDX <https://spdx.org/licenses/>`_ licenses.
    - ``tags``: a list of tags. These have the same character requirements as ``namespace`` and ``name``.
    - ``repository``: URL of originating SCM repository.
    - ``documentation``: URL for online docs.
    - ``homepage``: URL for project homepage.
    - ``issues``: URL for issue tracker.

Role Names
==========

For roles within a collection the Galaxy import process requires that role names:

- Contain only lowercase alphanumeric characters, plus ``_``
- Start with an alpha character

The directory name of the role is used as the role name, so therefore the directory name must comply with the
above rules. If a role name is encountered that does not match the above rules, the collection import will fail. 

.. note::

    For roles imported into Galaxy directly from a GitHub repository, setting the ``role_name`` value in the role's
    metadata overrides the role name used by Galaxy. For collections, that value is ignored. When importing a
    collection, Galaxy uses the role directory as the name of the role and ignores the ``role_name`` metadata value.

.. _building_collections:

Building and Distributing Collections
=====================================

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

Upload From the Galaxy Website 
``````````````````````````````

Go to the `My Content </my-content/namespaces>`_ page, and click the *Add Content* button on one of your namespaces. From 
the *Add Content* dialogue, click *Upload New Collection*, and select the collection archive file from your local
filesystem.

When uploading collections it doesn't actually matter which namespace you select. The collection will be uploaded to the
namespace specified in the collection metadata specified in the ``galaxy.yml`` file. If you're not an owner of the
namespace, the upload request will fail.

Once a collection has been uploaded and accepted by Galaxy, you will be redirected to the My Imports page, displaying output from the
import process, including any errors or warnings about the metadata and content contained in the collection.

Upload Using Mazer
``````````````````

Collection artifacts can be uploaded with Mazer, as shown in the following example: 

.. code-block:: bash

    mazer publish --api-key=SECRET path/to/namespace_name-collection_name-1.0.12.tar.gz

The above will trigger an import process, just as if the collection had been uploaded through the Galaxy website. Use the My Imports
page to view the output from the import process.

Your API key can be found on `the preferences page in Galaxy </me/preferences>`_.

To learn more about Mazer, view :doc:`../mazer/index`.


Collection Versions
```````````````````

Once a version of a collection has been uploaded it cannot be deleted or modified, so make sure that everything looks okay before
uploading. The only way to change a collection is to release a new version. The latest version of a collection (by highest version number)
will be the version displayed everywhere in Galaxy; however, users will still be able to download older versions.
