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
from galaxy.worker import utils
from galaxy.worker import exceptions as exc

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

        name = None
        original_name = None

        if not self.data.path:
            name = repo.name
            original_name = repo.name

        if self.data.name:
            name = self.data.name

        if self.data.original_name:
            original_name = self.data.original_name

        # Check name
        if not re.match('^[\w-]+$', name):
            raise exc.TaskError(
                'Invalid name: "{0}", only aplhanumeric characters, '
                '"-" and "_" symbols are allowed.'.format(name))

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

        if is_created:
            self.log.debug(
                'Created new Content instance: '
                'id={} content_type="{}", name="{}"'
                .format(obj.id, self.data.content_type, self.data.name))
        else:
            self.log.debug(
                'Found Content instance: '
                'id={}, content_type="{}", name="{}"'
                .format(obj.id, self.data.content_type, self.data.name))
        return obj

    def update_content(self, content):
        content.description = self.data.description or ''
        content.metadata = self.data.metadata

    def _add_readme(self, content):
        readme, readme_html, readme_type = utils.get_readme(
            self.ctx.github_token, self.ctx.github_repo)
        content.readme = readme
        content.readme_html = readme_html
        content.readme_type = readme_type
