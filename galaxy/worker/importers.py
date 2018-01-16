import logging

import pytz
from django.utils import timezone

from galaxy.main import models
from galaxy.worker import utils
from galaxy.worker import exceptions as exc


LOG = logging.getLogger(__name__)


class RoleImporter(object):
    MAX_TAGS_COUNT = 20

    def __init__(self, context, loader):
        self.ctx = context
        self.loader = loader

    def import_content(self):
        data = self.loader.load()
        role = self._create_content(data)

        self._update_role(role, data)

        role.is_valid = True
        role.imported = timezone.now()
        role.clean()
        role.save()

        return role

    def _create_content(self, data):
        repository = self.ctx.repository

        LOG.debug('Creating Content instance: content_type={0}, '
                  'namespace={1}, name={2}'
                  .format(data.content_type.value,
                          repository.github_user,
                          data.name))

        obj, is_created = models.Content.objects.get_or_create(
            # FIXME(cutwater): Use in-memory cache for content types
            content_type=models.ContentType.get(data.content_type),
            repository=repository,
            name=data.name,
            defaults={
                'namespace': repository.github_user,
                'is_valid': False,
            }
        )
        return obj

    def _update_role(self, role, role_data):
        gh_repo = self.ctx.github_repo

        role.description = role_data.description or gh_repo.description
        role.author = role_data.author
        role.company = role_data.company
        role.license = role_data.license
        role.min_ansible_version = role_data.min_ansible_version
        role.min_ansible_container_version = \
            role_data.min_ansible_container_version
        role.github_branch = role_data.github_branch
        role.github_default_branch = gh_repo.default_branch
        role.role_type = role_data.role_type.value
        role.container_yml = role_data.container_yml
        role.issue_tracker_url = role_data.issue_tracker_url

        if role.issue_tracker_url == "" and gh_repo.has_issues:
            role.issue_tracker_url = gh_repo.html_url + '/issues'

        self._add_role_videos(role, role_data.video_links)
        self._add_tags(role, role_data.tags)
        self._add_platforms(role, role_data.platforms)
        self._add_cloud_platforms(role, role_data.cloud_platforms)
        self._add_dependencies(role, role_data.dependencies)
        self._add_readme(role)
        self._update_role_versions(role)

    def _add_role_videos(self, role, videos):
        role.videos.all().delete()
        for video in videos:
            role.videos.create(
                url=video['url'],
                description=video['title'])

    def _add_tags(self, role, tags):
        if not tags:
            LOG.warn('No galaxy tags found in metadata')
        elif len(tags) > self.MAX_TAGS_COUNT:
            LOG.warn('Found more than {0} galaxy tags in metadata. '
                     'Only first {0} will be used'.format(self.MAX_TAGS_COUNT))
            tags = role.tags[:self.MAX_TAGS_COUNT]

        for tag in tags:
            role.tags.get_or_create(
                name=tag,
                defaults={'description': tag, 'active': True})

        # Remove tags no longer listed in the metadata
        for tag in role.tags.all():
            if tag.name not in tags:
                role.tags.remove(tag)

    def _add_platforms(self, role, platforms):
        if role.role_type not in (role.CONTAINER, role.ANSIBLE):
            return
        if not platforms:
            LOG.warn('No platforms found in meta data')
            return

        new_platforms = []
        for platform in platforms:
            name = platform.name
            versions = platform.versions
            if 'all' in versions:
                platform_objs = models.Platform.objects.filter(name=name)
                if not platform_objs:
                    LOG.warn(u'Invalid platform: "{}-all", skipping.'
                             .format(name))
                    continue
                for p in platform_objs:
                    role.platforms.add(p)
                    new_platforms.append((name, p.release))
                continue

            for version in versions:
                try:
                    p = models.Platform.objects.get(name=name, release=version)
                except models.Platform.DoesNotExist:
                    LOG.warn(u'Invalid platform: "{}-{}", skipping.'
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
                LOG.warn(u'Invalid cloud platform: "{0}", skipping'
                         .format(name))
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
                    LOG.error(
                        u"Error loading dependencies {}".format(e))
                    raise Exception(
                        u"Role dependency not found: {}.{}".format(
                            dep.namespace, dep.name))
            except Exception as e:
                LOG.warn(u'Error parsing dependency {}'.format(e))

        for dep in role.dependencies.all():
            if (dep.namespace, dep.name) not in new_deps:
                role.dependencies.remove(dep)

    def _add_readme(self, role):
        readme, readme_html, readme_type = utils.get_readme(
            self.ctx.github_token, self.ctx.github_repo)
        role.readme = readme
        role.readme_html = readme_html
        role.readme_type = readme_type

    def _update_role_versions(self, role):
        LOG.info('Adding repo tags as role versions')
        repo = self.ctx.github_repo
        git_tag_list = []
        try:
            git_tag_list = repo.get_tags()
            for tag in git_tag_list:
                rv, created = models.ContentVersion.objects.get_or_create(
                    name=tag.name, role=role)
                rv.release_date = tag.commit.commit.author.date.replace(
                    tzinfo=pytz.UTC)
                rv.save()
        except Exception as e:
            LOG.warn(u"An error occurred while importing repo tags: {}"
                     .format(e))

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
