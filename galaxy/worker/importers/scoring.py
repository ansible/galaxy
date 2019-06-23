# (c) 2012-2019, Ansible by Red Hat
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

from galaxy import constants

# TODO: pull out of here and importer/loaders/role into constants
BASE_SCORE = 50.0
CONTENT_SEVERITY_TYPE = 'content'
METADATA_SEVERITY_TYPE = 'metadata'


def score_collection(contents):
    """Calculate collection quality score from content scores.

    :param contents: list of content in json
    :return: quality score number for collection
    """

    coll_points = 0.0
    count = 0
    for content in contents:
        if content['scores']:
            coll_points += content['scores']['quality']
            count += 1
    quality_score = None if count == 0 else coll_points / count
    return quality_score


def score_contents(contents, log=None):
    """Calcuate quality score for list of contents.

    :param contents: list of importer.models.Content
    :return: scored list of importer.models.Content
    """

    scored_contents = []
    for content in contents:
        if content.content_type == constants.ContentType.ROLE:
            content = _score(content)
        else:
            content.scores = None
        scored_contents.append(content)
    return scored_contents


def _score(content):
    """Calculate score for content from running total of score violations.

    Score violations can come from importer (via linters),
    and from worker (via database validation).
    """

    content_w = content.scores.get(CONTENT_SEVERITY_TYPE, 0.0)
    content_score = max(0.0, (BASE_SCORE - content_w) / 10)

    metadata_w = content.scores.get(METADATA_SEVERITY_TYPE, 0.0)
    metadata_score = max(0.0, (BASE_SCORE - metadata_w) / 10)

    content.scores = {
        'content': content_score,
        'metadata': metadata_score,
        'compatibility': None,
        'quality': sum([content_score, metadata_score]) / 2.0
    }
    return content
