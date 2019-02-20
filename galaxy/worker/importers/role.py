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

from __future__ import absolute_import

from galaxy import common
from galaxy import constants
from galaxy.main import models

from . import base


class RoleImporter(base.ContentImporter):

    def update_content(self, content):
        super(RoleImporter, self).update_content(content)
        gh_repo = self.ctx.github_repo

        if not content.description:
            content.description = gh_repo.description

        role_meta = self.data.role_meta

        content.author = role_meta['author']
        content.company = role_meta['company']
        content.license = role_meta['license']
        content.min_ansible_version = role_meta['min_ansible_version']
        content.min_ansible_container_version = \
            role_meta['min_ansible_container_version']
        content.github_branch = role_meta['github_branch']
        content.github_default_branch = gh_repo.default_branch
        content.role_type = role_meta['role_type']
        content.container_yml = self.data.metadata['container_meta']

        self._add_role_videos(content, role_meta['video_links'])
        self._add_tags(content, role_meta['tags'])
        self._add_platforms(content, role_meta['platforms'])
        self._add_cloud_platforms(content, role_meta['cloud_platforms'])
        self._add_dependencies(content, role_meta['dependencies'])

    def translate_content_name(self, name):
        return common.sanitize_content_name(name)

    def _add_role_videos(self, role, videos):
        role.videos.all().delete()
        for video in videos:
            role.videos.create(
                url=video.url,
                description=video.description)

    def _add_tags(self, role, tags):
        for tag in tags:
            db_tag, _ = models.Tag.objects.get_or_create(
                name=tag,
                defaults={'description': tag, 'active': True}
            )
            role.tags.add(db_tag)

        # Remove tags no longer listed in the metadata
        for tag in role.tags.all():
            if tag.name not in tags:
                role.tags.remove(tag)

    def _add_platforms(self, role, platforms):
        if role.role_type not in (constants.RoleType.CONTAINER,
                                  constants.RoleType.ANSIBLE):
            return
        for platform in platforms:
            role.platforms.add(platform)

        # Remove platforms/versions that are no longer listed in the metadata
        for db_platform in role.platforms.all():
            if db_platform not in platforms:
                role.platforms.remove(db_platform)

    def _add_cloud_platforms(self, role, cloud_platforms):
        cloud_platforms = set(cloud_platforms)

        for cloud_platform in cloud_platforms:
            role.cloud_platforms.add(cloud_platform)

        # Remove cloud platforms that are no longer listed in the metadata
        for db_cloud_platform in role.cloud_platforms.all():
            if db_cloud_platform not in cloud_platforms:
                role.cloud_platforms.remove(db_cloud_platform)

    def _add_dependencies(self, role, dependencies):
        if role.role_type not in (constants.RoleType.CONTAINER,
                                  constants.RoleType.ANSIBLE):
            return
        for dep_role in dependencies:
            role.dependencies.add(dep_role)

        # Remove dependencies no longer in the metadata
        for dep in role.dependencies.all():
            if (dep.namespace.name, dep.name) not in dependencies:
                role.dependencies.remove(dep)
