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
from galaxy.main import models

# TODO: move this to common
from galaxy.importer.utils.lint import LintRecord


# TODO: pull out of here and importer/loaders/role into constants
BASE_SCORE = 50.0
SEVERITY_TO_WEIGHT = {
    0: 0.0,
    1: 0.75,
    2: 1.25,
    3: 2.5,
    4: 5.0,
    5: 10.0,
}
CONTENT_SEVERITY_TYPE = 'content'
METADATA_SEVERITY_TYPE = 'metadata'

METADATA_SEVERITY = {
    'importer_importer101': 3,
    'importer_importer102': 3,
    'importer_importer103': 4,
}


def validate_contents(content_list, log=None):
    """Database checks for content-level metadata.

    :param content_list: list of importer.models.Content
    :return: validated list of importer.models.Content
    """

    validated_contents = []
    for content in content_list:
        validator = ContentValidator(content, log)
        validated_contents.append(validator.check_contents())
    return validated_contents


class ContentValidator():
    def __init__(self, content, log):
        self.content = content
        self.log = log

    def check_contents(self):
        if self.content.content_type == constants.ContentType.ROLE:
            self._check_role()
            self._score()
        else:
            self.content.scores = None

        return self.content

    def _check_role(self):
        """Database check role_meta platforms, cloud platforms, dependencies.

        Checks edit role_meta to values present in database.
        Role can be part of a collection or repository.

        :param content: importer.models.Content
        :return: content with role_meta that is validated against database
        """

        self.log.info(
            f'===== DATABASE CHECKS - ROLE: {self.content.name} =====')
        self._check_role_platforms()
        self._check_role_cloud_platforms()
        self._check_role_dependencies()
        self.log.info(' ')

    def _check_role_platforms(self):
        """Check each role metadata platform is present in database."""
        self.log.info('Checking role platforms')
        confirmed_platforms = []

        for platform in self.content.role_meta['platforms']:
            name = platform.name
            versions = platform.versions
            if 'all' in versions:
                platform_objs = models.Platform.objects.filter(
                    name__iexact=name
                )
                if not platform_objs:
                    msg = f'Invalid platform: "{name}-all", skipping.'
                    self._on_lint_issue('IMPORTER101', msg)
                    continue
                for p in platform_objs:
                    confirmed_platforms.append(p)
                continue

            for version in versions:
                try:
                    p = models.Platform.objects.get(
                        name__iexact=name, release__iexact=str(version)
                    )
                except models.Platform.DoesNotExist:
                    msg = f'Invalid platform: "{name}-{version}", skipping.'
                    self._on_lint_issue('IMPORTER101', msg)
                else:
                    confirmed_platforms.append(p)

        self.content.role_meta['platforms'] = confirmed_platforms

    def _check_role_cloud_platforms(self):
        """Check each role metadata cloud platform is present in database."""
        self.log.info('Checking role cloud platforms')
        confirmed_platforms = []

        for name in self.content.role_meta['cloud_platforms']:
            try:
                c = models.CloudPlatform.objects.get(name__iexact=name)
            except models.CloudPlatform.DoesNotExist:
                msg = f'Invalid cloud platform: "{name}", skipping.'
                self._on_lint_issue('IMPORTER102', msg)
            else:
                confirmed_platforms.append(c)

        self.content.role_meta['cloud_platforms'] = confirmed_platforms

    def _check_role_dependencies(self):
        """Check each role metadata role dependency is present in database."""
        self.log.info('Checking role dependencies')
        confirmed_deps = []

        for dep in self.content.role_meta['dependencies'] or []:
            try:
                dep_role = models.Content.objects.get(
                    namespace__name=dep.namespace, name=dep.name)
                confirmed_deps.append(dep_role)
            except Exception:
                msg = 'Error loading dependency: "{}"'.format(
                    '.'.join([d for d in dep]))
                self._on_lint_issue('IMPORTER103', msg)

        self.content.role_meta['dependencies'] = confirmed_deps

    def _on_lint_issue(self, rule_id, rule_desc):
        """Appends linter violations of type metadata to content."""
        lint_record = LintRecord(
            type='importer',
            code=rule_id,
            message=rule_desc,
            score_type=METADATA_SEVERITY_TYPE,
            severity=METADATA_SEVERITY[f'importer_{rule_id.lower()}'],
        )

        self.content.scores[METADATA_SEVERITY_TYPE] = (
            self.content.scores.get(METADATA_SEVERITY_TYPE, 0.0)
            + SEVERITY_TO_WEIGHT[lint_record.severity])
        self.log.warning(rule_desc,
                         extra={'lint_record': lint_record})

    def _score(self):
        """Calculate content score from running total of score violations.

        Score violations can come from importer (via linters),
        and from worker (via database validation).
        """

        content_w = self.content.scores.get(CONTENT_SEVERITY_TYPE, 0.0)
        content_score = max(0.0, (BASE_SCORE - content_w) / 10)

        metadata_w = self.content.scores.get(METADATA_SEVERITY_TYPE, 0.0)
        metadata_score = max(0.0, (BASE_SCORE - metadata_w) / 10)

        # TODO: rename scores and score_stats
        self.content.scores = {
            'content': content_score,
            'metadata': metadata_score,
            'compatibility': None,
            'quality': sum([content_score, metadata_score]) / 2.0
        }
