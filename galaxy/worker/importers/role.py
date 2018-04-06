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

import pytz

from galaxy.main import models
from galaxy.worker import exceptions as exc

from . import base


class RoleImporter(base.ContentImporter):
    MAX_TAGS_COUNT = 20

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
        content.issue_tracker_url = role_meta['issue_tracker_url']
        content.container_yml = self.data.metadata['container_meta']

        if content.issue_tracker_url == "" and gh_repo.has_issues:
            content.issue_tracker_url = gh_repo.html_url + '/issues'

        self._add_role_videos(content, role_meta['video_links'])
        self._add_tags(content, role_meta['tags'])
        self._add_platforms(content, role_meta['platforms'])
        self._add_cloud_platforms(content, role_meta['cloud_platforms'])
        self._add_dependencies(content, role_meta['dependencies'])
        self._add_readme(content)
        self._update_role_versions(content)

    def _add_role_videos(self, role, videos):
        role.videos.all().delete()
        for video in videos:
            role.videos.create(
                url=video['url'],
                description=video['title'])

    def _add_tags(self, role, tags):
        if not tags:
            self.log.warning('No galaxy tags found in metadata')
        elif len(tags) > self.MAX_TAGS_COUNT:
            self.log.warning(
                'Found more than {0} galaxy tags in metadata. '
                'Only first {0} will be used'
                .format(self.MAX_TAGS_COUNT))
            tags = role.tags[:self.MAX_TAGS_COUNT]

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
        if role.role_type not in (role.CONTAINER, role.ANSIBLE):
            return
        if not platforms:
            self.log.warning('No platforms found in metadata')
            return

        new_platforms = []
        for platform in platforms:
            name = platform.name
            versions = platform.versions
            if 'all' in versions:
                platform_objs = models.Platform.objects.filter(name=name)
                if not platform_objs:
                    self.log.warning(
                        u'Invalid platform: "{}-all", skipping.'.format(name))
                    continue
                for p in platform_objs:
                    role.platforms.add(p)
                    new_platforms.append((name, p.release))
                continue

            for version in versions:
                try:
                    p = models.Platform.objects.get(name=name, release=version)
                except models.Platform.DoesNotExist:
                    self.log.warning(
                        u'Invalid platform: "{}-{}", skipping.'
                        .format(name, version))
                else:
                    role.platforms.add(p)
                    new_platforms.append((name, p.release))

        # Remove platforms/versions that are no longer listed in the metadata
        for platform in role.platforms.all():
            platform_key = (platform.name, platform.release)
            if platform_key not in new_platforms:
                role.platforms.remove(platform)

    def _add_cloud_platforms(self, role, cloud_platforms):
        cloud_platforms = set(cloud_platforms)

        # Remove cloud platforms that are no longer listed in the metadata
        for platform in role.cloud_platforms.all():
            if platform.name not in cloud_platforms:
                role.cloud_platforms.remove(platform)

        # Add new cloud platforms
        for name in cloud_platforms:
            try:
                platform = models.CloudPlatform.objects.get(name=name)
            except models.CloudPlatform.DoesNotExist:
                self.log.warning(
                    u'Invalid cloud platform: "{0}", skipping'.format(name))
                continue
            role.cloud_platforms.add(platform)

    def _add_dependencies(self, role, dependencies):
        if role.role_type not in (role.CONTAINER, role.ANSIBLE):
            return
        if not dependencies:
            return

        new_deps = []
        for dep in dependencies:
            try:
                try:
                    dep_role = models.Content.objects.get(
                        namespace=dep.namespace, name=dep.name)
                    role.dependencies.add(dep_role)
                    new_deps.append(dep)
                except Exception as e:
                    self.log.error(
                        u"Error loading dependencies {}".format(e))
                    raise Exception(
                        u"Role dependency not found: {}.{}".format(
                            dep.namespace, dep.name))
            except Exception as e:
                self.log.warning(
                    u'Error parsing dependency {}'.format(e))

        for dep in role.dependencies.all():
            if (dep.namespace, dep.name) not in new_deps:
                role.dependencies.remove(dep)

    def _update_role_versions(self, role):
        self.log.info('Adding repo tags as role versions')
        repo = self.ctx.github_repo
        git_tag_list = []
        try:
            git_tag_list = repo.get_tags()
            for tag in git_tag_list:
                rv, created = models.ContentVersion.objects.get_or_create(
                    name=tag.name, content=role)
                rv.release_date = tag.commit.commit.author.date.replace(
                    tzinfo=pytz.UTC)
                rv.save()
        except Exception as e:
            self.log.warning(
                u"An error occurred while importing repo tags: {}".format(e))

        if git_tag_list:
            remove_versions = []
            try:
                for version in role.versions.all():
                    found = False
                    for tag in git_tag_list:
                        if tag.name == version.name:
                            found = True
                            break
                    if not found:
                        remove_versions.append(version.name)
            except Exception as e:
                raise exc.TaskError(
                    u"Error identifying tags to remove: {}".format(e))

            if remove_versions:
                try:
                    for version_name in remove_versions:
                        models.ContentVersion.objects.filter(
                            name=version_name, role=role).delete()
                except Exception as e:
                    raise exc.TaskError(
                        u"Error removing tags from role: {}".format(e))
