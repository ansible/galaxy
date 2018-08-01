********************
Development Workflow
********************

Issues
======

Status
------

New
    The issue was just created, requires triage.
Incomplete
    The issue is waiting on input from the reporter.
Confirmed
    The issue was reproduced or confirmed as a genuine bug.
Fix Committed
    The fix has been merged into a development or release branch.
Fix Released
    The fix has been released.
Invalid
    Not a bug.
Won’t Fix
    This is a valid issue, but we don’t intend to fix that.
Duplicate
    This issue contains similar information to another issue.

Importance \ Priority
---------------------

Importance labels should be set when the status reaches Confirmed stage.
It is a combination of short-term impact (unavailability of a feature),
long-term impact (data corruption, security breach), number of people affected,
and presence of a documented workaround. Use these as guidelines:

Critical
    Data corruption / complete failure affecting most users, no workaround.
High
    Data corruption / complete failure affecting most users, with workaround.
    Failure of a significant feature, no workaround.
Medium
    Failure of a significant feature, with workaround.
    Failure of a fringe feature, no workaround.
Low
    Small issue with an easy workaround.
    Any other insignificant bug.
Wishlist
    Not really a bug, but a suggested improvement.

Issues Lifecycle
----------------

.. todo: Insert picture.

All new issues submitted by community users initially should have status **New**.

If issue is lacking information to reproduce or assess importance of the issue,
it’s status should be changed to **Incomplete**.

Once the issue is reproduced it should be prioritized and assigned
status **Confirmed**.

When the issue is merged into development or release branch it’s status s
hould be updated to **Fix Committed**.

*Note: Since Galaxy is a community project, we should be careful about
closing issues. Closing issues before release leads to users confusion,
because it’s unclear whether the fix is applied or not.*

When the issue is released, it should be updated with status **Fix Released**,
the milestone the milestone/version it was fixed in and then closed.

If the issue is closed with status **Invalid** or **Won’t fix** it should
include comment that describes motivation behind the decision.

Branching strategy
==================

Branch ``devel``
----------------

``devel`` branch is the default branch in Galaxy repository. It is used
as a primary merge target for all feature and bugfix pull requests.

Branch  ``master``
------------------

``master`` branch points to a latest release version, which is running
on `Galaxy`_ web site.

Release branches
----------------

Release branches ``release/x.x.x``, whhere ``x.x.x`` is for next release version,
are used for release preparation. Pull requests that are intended to be
released as a part of next release version should be merged to release branch
following :ref:`release_process`.

Backport process
================

Prepare your devel, stable, and feature branches::

    git fetch upstream
    git checkout -b backport/3.0/[PR_NUMBER_FROM_DEVEL] upstream/release/3.0

Cherry pick the relevant commit SHA from the devel branch into your
feature branch, handling merge conflicts as necessary::

    git cherry-pick -x [SHA_FROM_DEVEL]


Add a changelog entry for the change, and commit it. Then push your feature
branch to your fork on GitHub::

    git push origin backport/3.0/[PR_NUMBER_FROM_DEVEL]


Submit the pull request for ``backport/3.0/[PR_NUMBER_FROM_DEVEL]`` against
the ``release/3.0`` branch.

Name your pull request accordingly to the original one.
Include a reference to the original pull request into description
in format (. Assign a ``backport`` label.

Example:

.. code-block:: none

    Improve breadcrumbs

    * Update header to accept icon parameter.
    * Hide breadcrumbs on small devices.
    * Make line under header extend width of page.

    Issue: #718
    Backport: #961

    (cherry picked from commit 459f13c0c39f65a99dc1736a0fa09250f37e86ea)


.. note: Update contributing policy to force users squash their
         changes before merge.

.. note: Check cherry-picker tool to automate backporting process.

.. _release_process:

Release process
===============

Merge ``release/<x.x.x>`` branch to master::

     git checkout master
     git merge -m "Release <x.x.x>" release/<x.x.x>

Tag merge commit as ``v<x.x.x>``::

     git tag -s -m "Release <x.x.x>"

Push merge commit and release tag to upstream repository::

     git push upstream master
     git push upstream v<x.x.x>


.. _Galaxy: https://galaxy.ansible.com
