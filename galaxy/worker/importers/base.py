# (c) 2012-2018, Ansible by Red Hat
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

import logging
import re

from django.utils import timezone

from galaxy.main import models
from galaxy.worker import exceptions as exc, utils


LOG = logging.getLogger(__name__)


class ContentImporter(object):

    def __init__(self, context, data, logger=None):
        self.ctx = context
        self.data = data
        self.log = logger or LOG

    def do_import(self):
        content = self.make_content()

        self.update_content(content)

        content.is_valid = True
        content.imported = timezone.now()
        content.clean()
        content.save()

        return content

    def make_content(self):
        repo = self.ctx.repository
        ns = repo.provider_namespace.namespace

        name = repo.name
        original_name = repo.name

        if self.data.name:
            name = self.data.name
        if self.data.original_name:
            original_name = self.data.original_name

        # Check name
        if not re.match('^[\w-]+$', name):
            raise exc.TaskError('Invalid name, only aplhanumeric characters, '
                                '"-" and "_" symbols are allowed.')

        obj, is_created = models.Content.objects.get_or_create(
            namespace=ns,
            # FIXME(cutwater): Use in-memory cache for content types
            content_type=models.ContentType.get(self.data.content_type),
            name=name,
            defaults={
                'original_name': original_name,
                'repository': repo,
                'is_valid': False,
            }
        )

        self._log_create_content(obj.id, is_created)

        return obj

    def update_content(self, content):
        content.description = self.data.description or ''
        content.metadata = self.data.metadata
        self._update_readme(content)

    def _update_readme(self, content):
        readme = self.data.readme
        repository = content.repository
        readme_obj = content.readme
        content.readme = None
        content.save()
        content.readme = utils.update_readme(
            repository, readme_obj, readme,
            self.ctx.github_client, self.ctx.github_repo)
        content.save()

    def _log_create_content(self, content_id, is_created):
        action = 'Created new' if is_created else 'Found'
        self.log.debug(
            '{action} Content instance: id={id}, content_type="{content_type}"'
            ', name="{name}"'.format(
                action=action, id=content_id,
                content_type=self.data.content_type, name=self.data.name))
