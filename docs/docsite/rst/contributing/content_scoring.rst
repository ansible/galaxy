.. _content_scoring:

***************
Content Scoring
***************

.. contents:: Topics


This topic describes how content is scored.

Scores displayed when browsing content are the average of
the content's Community Score and Quality Score.
Content Scoring is in early iterations, to be improved with
user feedback and future additions to ansible-lint.

Overall Score
=============

The overall score is a combination of the community score, the quality score and the number of surveys that have been submitted for a role.
This number is calculated as the weighted average of the community and quality scores. If there are fewer than three surveys submitted the
quality score has a slightly higher weight. If there are three or more surveys submitted the community and quality scores have an identical
weight. For more details on this formula see `PR #1406 <https://github.com/ansible/galaxy/pull/1406>`_.

Community Score
===============

* The Community Score is calculated from community surveys submitted by Galaxy users
  - Each question receives an value of 0 to 5 points based on how the user answers it
  - The total score is a simple average of the value of all of the questions
  - Questions that are unanswered are not included in the average
* Maximum score of ``5.0``

Quality Score
=============

* The Quality Score is based on analysis from ``yamllint`` ``ansible-lint`` and import-time checks
* Maximum score is ``5.0``
* The Quality Score is the average of `Syntax Score <syntax-score_>`_ and `Metadata Score <metadata-score_>`_

.. note::
   Scoring is only done at import, to re-score please re-import

Linters Used
------------

* ``yamllint`` is run with a `custom config <https://github.com/ansible/galaxy/blob/devel/galaxy/importer/linters/yamllint.yaml>`_
* ``ansible-lint`` is run using its default rules, for information on how to fix Ansible Lint issues, see the descriptions in the `default rules <https://docs.ansible.com/ansible-lint/rules/default_rules.html>`_
* import-time checks reference the Galaxy database, checking for valid platforms, valid cloud platforms, and loadable dependencies

.. _syntax-score:

Syntax Score
------------
Linter issues applied to the Syntax Score are ``yamllint`` and non-metadata ``ansible-lint``

Each linter issue is subtracted from a max score of ``5.0``:

* Issue severity of "VERY_HIGH" reduces the score by ``1.0``
* Issue severity of "HIGH" reduces the score by ``0.5``
* Issue severity of "MEDIUM" reduces the score by ``0.25``
* Issue severity of "LOW" reduces the score by ``0.125``
* Issue severity of "VERY_LOW" reduces the score by ``0.075``
* Issue severity of "INFO" does not reduce the score

.. _metadata-score:

Metadata Score
--------------
Linter issues applied to the Syntax Score are metadata ``ansible-lint`` and import-time checks

Each linter issue is subtracted from a max score of ``5.0``:

* Issue severity of "VERY_HIGH" reduces the score by ``1.0``
* Issue severity of "HIGH" reduces the score by ``0.5``
* Issue severity of "MEDIUM" reduces the score by ``0.25``
* Issue severity of "LOW" reduces the score by ``0.125``
* Issue severity of "VERY_LOW" reduces the score by ``0.075``
* Issue severity of "INFO" does not reduce the score
