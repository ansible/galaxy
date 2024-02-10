.. _galaxy_namespaces:

*****************
Galaxy Namespaces
*****************

.. contents:: Topics


This topic describes how to Galaxy namespaces.

Managing Namespaces
===================

Ansible roles and collections are associated with a Galaxy namespace. In other words, a role is imported into a namespace, and a collection is
uploaded or published to a namespace. When referencing a role or collection for download and install the namespace becomes part of the reference
in the form ``namespace.[role | collection]_name``.

The first time you log into Galaxy using your GitHub credentials a namespace is created for your GitHub username automatically. For name
limiations view :ref:`galaxy_namespace_limitations`. To request additional namespaces view :ref:`galaxy_namespace_requests`.

Adding GitHub Organizations to a Namespace
------------------------------------------

Role repositories from multiple GitHub organizations can be imported into a Galaxy namespace. To add additional GitHub organizations,
on My Content, expand the menu for the namespace, and choose *Edit Properties*, as shown here:

.. image:: mycontent-08.png

On the next page, scroll to the bottom of the page, where a list of available GitHub organizations is displayed. It's labeled
*Provider Namespaces*, and represents the list of namespaces or ogranizations you have access to in GitHub.

As indicated in the image below, click on an organization to select it and add it to the *Selected Provider Namespaces* on the right.
Clicking the *X* next to the name on the right will remove it.

.. image:: mycontent-09.png

At the top of the list of Provider namespace is a search box. If you don't see an organization listed, try typing the name in the
box and pressing Enter. (In case the organization is still missing, please ensure that the Ansible Galaxy GitHub app has access to
your organization as described in :ref:`updating_github_permissions`.)

Click the *Save* button at the bottom of the page to update the namespace with your changes, as shown below:

.. image:: mycontent-10.png

.. note::
    Adding GitHub organizations to a namespace is only required when importing role repositories from GitHub. It is not required
    for uploading or publishing collections.

Adding Administrators to a Namespace
------------------------------------

Multiple Galaxy users can own or have administration rights to a namespace. To add additional owners to a namespace, expand the namespace
menu on My Content, and choose *Edit Properties*, as depicted below:

.. image:: mycontent-11.png

On the next page, scroll toward the bottom of the page, where a list of *Namespace Owners* appears. Use the search box to find
specific users by Galaxy username. Click on a user to add them to the list of *Selected Galaxy Users* on the right, or click the *X*
next to the username to remove them from the list. The image below provides an example:

.. image:: mycontent-12.png

Anyone in the list of owners can import content into the namespace. They can also modify properties of the namespace, remove content,
and disable the namespace altogether, removing content from search results, and making it unavailable for download.

After making changes to the list of owners, click the *Save* button at the bottom of the page to update the namespace with your
changes, as shown below:

.. image:: mycontent-10.png

.. _galaxy_namespace_limitations:

Namespace Limitations
---------------------

Namespace names in Galaxy are limited to lowercase word characters (i.e., a-z, 0-9) and '_', must have a minimum length of 2
characters, and cannot start with an '_'. No other characters are allowed, including '.', '-', and space.

The first time you log into Galaxy, the server will create a Namespace for you, if one does not already exist, by converting
your username to lowercase, and replacing any '-' characters with '_'.

.. _galaxy_namespace_requests:

Requesting Additional Namespaces
--------------------------------

In order to protect against copyright and trademark infringements, new Galaxy namespaces can only be created by submitting a
request to the Galaxy team. A team member will review the request and create the new namespace within 1 to 2 business days.

When submitting a request, please include a link to the GitHub organization and a list of Galaxy usernames to be given ownership
rights to the new namespace. `Click here to submit a request now <https://github.com/ansible/galaxy/issues/new?template=New_namespace.md>`_.
