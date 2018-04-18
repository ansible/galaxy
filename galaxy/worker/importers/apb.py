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

from . import base

from galaxy.main import models
from galaxy import constants


class APBImporter(base.ContentImporter):

    def update_content(self, content):
        super(APBImporter, self).update_content(content)
        role_meta = self.data.role_meta
        self._add_readme(content)
        self._add_tags(content, role_meta['tags'])

    def _add_tags(self, content, tags):
        if not tags:
            self.log.warning('No tags found in metadata')
        elif len(tags) > constants.MAX_TAGS_COUNT:
            self.log.warning(
                'Found more than {0} tags in metadata. '
                'Only first {0} will be used'
                .format(constants.MAX_TAGS_COUNT))
            tags = content.tags[:constants.MAX_TAGS_COUNT]

        for tag in tags:
            db_tag, _ = models.Tag.objects.get_or_create(
                name=tag,
                defaults={'description': tag, 'active': True}
            )
            content.tags.add(db_tag)

        # Remove tags no longer listed in the metadata
        for tag in content.tags.all():
            if tag.name not in tags:
                content.tags.remove(tag)
