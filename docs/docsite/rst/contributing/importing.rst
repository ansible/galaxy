.. _importing_content:

*****************
Importing Content
*****************

.. contents:: Topics


This topic describes how to import Ansible content into the public Galaxy web site.

.. _import_get_started:

Getting Started
===============

At present, Galaxy only imports content from `GitHub <https://github.com>`_, and importing content to the `public Galaxy server <https://galaxy.ansible.com>`_
requires authentication using a GitHub account.

Logging In
----------

Before you can import content, you'll need to first authenticate with the Galaxy server using your GitHub account. Start by clicking
the *Login* link, as shown below:

.. image:: login-01.png

Next, click the GitHub logo, as indicated in the image below:

.. image:: login-02.png

The first time you authenticate using your GitHub credentials, GitHub will present a page similar to the following asking you to grant
permissions to Galaxy:

.. image:: login-03.png

Galaxy requires access to your email address, in case an admin needs to reach out to you, read-write access to public repositories,
using the ``public_repo`` scope, and read access to your organizations and teams. Galaxy will never write or commit anything to a
repository. It needs access to public repositories so that it can read commits and the list of collaborators.

Be sure to click the *Grant* button next to each organization that contains Ansible content you want to import into Galaxy. The following
image shows the *Grant* button, after clicking it, you'll see a green checkmark to the right of the ogranization name, indicating that
Galaxy can access public repositories within the organization:

.. image:: login-04.png

After granting access to each organization, click the green button at the bottom of the page to authorize Galaxy to access your peronsal
GitHub namespace and continue, as indicated in the image below:

.. image:: login-05.png

Once you complete the above, you'll be taken back to the Galaxy web site, where you'll see the *My Content* and *My Imports* menu options
available, as depicted below:

.. image:: login-06.png

Updating GitHub Permissions
---------------------------

If you need to change the permission settings for a GitHub organization, log into `GitHub <https://github.com>`_, and navigate to
*Settings*, and *Applications*. Click the *Authorized Oauth Apps* tab, as depicted below:

.. image:: update-01.png

Next, click the name of the Ansible Galaxy app, as indicated in the image below. This will take you to the permissions page for the
app, where you can Grant permissions to individual organizations:

.. image:: update-02.png

As the image below indicats, click the *Grant* button next to each organization that Galaxy should have read access to. This will allow
Galaxy to import content from the organization:

.. image:: update-03.png

If you wish to revoke Galaxy access to an organization, click the *Revoke* button. This will remove all permissions. To reset permissions,
logout and log back into Galaxy using your GitHub credentials, and GitHub will present the permissions page, where you can grant access
to your organizations, and authorize access to your GitHub namespace, as discussed above in :ref:`import_get_started`.



Web Interface
=============




Travis CI
=========
