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
                    # TODO: add 'IMPORTER101' linter violation here
                    msg = f'Invalid platform: "{name}-all", skipping.'
                    self.log.warning(msg)
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
                    # TODO: add 'IMPORTER101' linter violation here
                    msg = f'Invalid platform: "{name}-{version}", skipping.'
                    self.log.warning(msg)
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
                # TODO: add 'IMPORTER102' linter violation here
                msg = f'Invalid cloud platform: "{name}", skipping.'
                self.log.warning(msg)
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
                # TODO: add 'IMPORTER103' linter violation here
                msg = 'Error loading dependency: "{}"'.format(
                    '.'.join([d for d in dep]))
                self.log.warning(msg)

        self.content.role_meta['dependencies'] = confirmed_deps
