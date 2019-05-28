.. _mazer_reference_publish:

publish
=======

.. program::mazer publish [options] [artifact path]

Publish installed content to Galaxy.

.. option:: --api-key

The Galaxy API key for authenticating.
The API key can be found at
https://galaxy.ansible.com/me/preferences

.. option:: --lockfile

Publish installed collections in collections lockfile format.

.. option:: --freeze

When used with --lockfile, publish installed collections in collections lockfile format with frozen versions.
