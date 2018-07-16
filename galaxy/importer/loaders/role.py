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

import collections
import os
import re

import six
import yaml

from ansible.playbook.role import requirement as ansible_req

from galaxy import constants
from galaxy.importer import models, linters
from galaxy.importer.loaders import base
from galaxy.importer import exceptions as exc
from galaxy.common import sanitize_content_name


ROLE_META_FILES = [
    'meta/main.yml', 'meta/main.yaml',
    'meta.yml', 'meta.yaml'
]


class RoleMetaParser(object):
    # TODO Role tags should contain lowercase letters and digits only

    VIDEO_REGEXP = {
        'google': re.compile(
            r'https://drive.google.com.*file/d/([0-9A-Za-z-_]+)/.*'),
        'vimeo': re.compile(
            r'https://vimeo.com/([0-9]+)'),
        'youtube': re.compile(
            r'https://youtu.be/([0-9A-Za-z-_]+)'),
    }
    VIDEO_EMBED_URLS = {
        'google': 'https://drive.google.com/file/d/{0}/preview',
        'vimeo': 'https://player.vimeo.com/video/{0}',
        'youtube': 'https://www.youtube.com/embed/{0}',
    }

    def __init__(self, metadata, logger=None):
        self.log = logger or base.default_logger
        self.metadata = self._get_galaxy_info(metadata)
        self.dependencies = self._get_dependencies(metadata)

    def _get_galaxy_info(self, metadata):
        if 'galaxy_info' in metadata:
            galaxy_info = metadata['galaxy_info']
            if not isinstance(galaxy_info, dict):
                raise exc.ContentLoadError(
                    "Expecting 'galaxy_info' in metadata to be a dictionary "
                    "or key:value mapping")
        else:
            self.log.warning("Missing 'galaxy_info' field in metadata.")
            galaxy_info = {}
        return galaxy_info

    def _get_dependencies(self, metadata):
        if 'dependencies' in metadata:
            dependencies = metadata['dependencies']
            if not isinstance(dependencies, collections.Sequence):
                raise exc.ContentLoadError(
                    "Expecting 'dependencies' in metadata to be a list")
        else:
            self.log.warning("Missing 'dependencies' field in metadata.")
            dependencies = []
        return dependencies

    def _validate_tag(self, tag):
        if not re.match(constants.TAG_REGEXP, tag):
            self.log.warning(
                "'{}' is not a valid tag. Tags must container lowercase "
                "letters and digits only. Skipping.".format(tag))
            return False
        return True

    def validate_strings(self):
        string_defaults = [
            ('author', 'your name', True),
            ('description', 'your description', True),
            ('company', 'your company', False),
            ('license', 'license', True)
        ]
        for key, value, required in string_defaults:
            if key not in self.metadata and required:
                exc.ContentLoadError("Missing required key {0} in metadata"
                                     .format(key))
            if key in self.metadata and value in self.metadata[key]:
                self.log.warning("Value of {0} has not been set in metadata."
                                 .format(key))

    def parse_tags(self):
        tags = []

        galaxy_tags = self.metadata.get('galaxy_tags', [])
        if isinstance(galaxy_tags, list):
            tags += galaxy_tags
        else:
            self.log.warning('Expected "galaxy_tags" in metadata to be a list')

        if 'categories' in self.metadata:
            self.log.warning(
                'Found "categories" in metadata. Update the metadata '
                'to use "galaxy_tags" rather than categories.')
            if isinstance(self.metadata['categories'], list):
                tags += self.metadata['categories']
            else:
                self.log.warning(
                    'Expected "categories" in meta data to be a list')

        tags = list(filter(self._validate_tag, tags))

        return tags

    def parse_platforms(self):
        meta_platforms = self.metadata.get('platforms')
        if not meta_platforms:
            return []
        if not isinstance(meta_platforms, collections.Sequence):
            raise exc.ContentLoadError(
                'Expected "platforms" in metadata to be a list.')

        platforms = []
        for idx, platform in enumerate(meta_platforms):
            try:
                name = platform['name']
            except KeyError:
                self.log.warning(
                    'No name specified for platform [{0}], skipping'
                    .format(idx))
                continue

            versions = platform.get('versions', ['all'])
            # TODO: Validate versions
            platforms.append(models.PlatformInfo(name, versions))
        return platforms

    def parse_cloud_platforms(self):
        cloud_platforms = self.metadata.get('cloud_platforms', [])
        if isinstance(cloud_platforms, six.string_types):
            cloud_platforms = [cloud_platforms]
        return cloud_platforms

    # TODO: Extend dependencies support with format used
    # in .galaxy-metadata.yml
    def parse_dependencies(self):
        if not self.dependencies:
            return []
        dependencies = []
        for dep in self.dependencies:
            dep = ansible_req.RoleRequirement.role_yaml_parse(dep)
            name = dep.get('name')
            if not name:
                raise exc.ContentLoadError(
                    'Unable to determine name for dependency')
            if '.' not in name:
                raise exc.ContentLoadError(
                    'Expecting dependency name format to match '
                    '"username.role_name", got {0}'
                    .format(dep['name']))
            dependencies.append(models.DependencyInfo(*name.rsplit('.', 2)))
        return dependencies

    def parse_videos(self):
        videos = []
        meta_videos = self.metadata.get('video_links', [])
        for video in meta_videos:
            if not isinstance(video, dict):
                self.log.warning(
                    'Expected item in video_links to be dictionary')
                continue
            if set(video) != {'url', 'title'}:
                self.log.warning("Expected item in video_links to contain "
                                 "only keys 'url' and 'title'")
                continue
            for name, expr in six.iteritems(self.VIDEO_REGEXP):
                match = expr.match(video['url'])
                if match:
                    file_id = match.group(1)
                    embed_url = self.VIDEO_EMBED_URLS[name].format(file_id)
                    videos.append(models.VideoLink(embed_url, video['title']))
                    break
            else:
                self.log.warning(
                    "URL format '{0}' is not recognized. "
                    "Expected it be a shared link from Vimeo, YouTube, "
                    "or Google Drive.".format(video['url']))
                continue
        return videos


class RoleLoader(base.BaseLoader):
    # (attribute name, default value)
    STRING_ATTRS = [
        ('description', ''),
        ('author', ''),
        ('company', ''),
        ('license', ''),
        ('min_ansible_version', None),
        ('min_ansible_container_version', None),
        ('issue_tracker_url', ''),
        ('github_branch', ''),
    ]
    CONTAINER_META_FILE = 'meta/container.yml'
    ANSIBLE_CONTAINER_META_FILE = 'container.yml'

    content_types = constants.ContentType.ROLE
    linters = (linters.Flake8Linter, linters.YamlLinter)

    def __init__(self, content_type, path, root, metadata_path, logger=None):
        """Initializes a `RoleLoader` object.

        :param str path: Path to role directory within repository.
        """
        super(RoleLoader, self).__init__(
            content_type, path, root, logger=logger)

        self.meta_file = metadata_path

    def load(self):
        meta = self._load_metadata()
        meta_parser = RoleMetaParser(meta, logger=self.log)
        galaxy_info = meta_parser.metadata

        meta_parser.validate_strings()

        # TODO: Refactoring required
        data = {}
        data.update(self._load_string_attrs(galaxy_info))

        container_yml_type, container_yml = self._load_container_yml()

        description = data.pop('description')

        data['role_type'] = self._get_role_type(
            galaxy_info, container_yml_type
        )
        data['tags'] = meta_parser.parse_tags()
        data['platforms'] = meta_parser.parse_platforms()
        data['cloud_platforms'] = meta_parser.parse_cloud_platforms()
        data['dependencies'] = meta_parser.parse_dependencies()
        data['video_links'] = meta_parser.parse_videos()
        readme = self._get_readme()

        name = self.name
        if galaxy_info.get('role_name'):
            name = sanitize_content_name(galaxy_info['role_name'])

        return models.Content(
            name=name,
            original_name=self.name,
            path=self.rel_path,
            content_type=self.content_type,
            description=description,
            role_meta=data,
            readme=readme,
            metadata={
                'container_meta': container_yml,
            }
        )

    def make_name(self):
        if self.rel_path:
            return os.path.basename(self.path)
        else:
            return None

    def _load_string_attrs(self, metadata):
        attrs = {}
        for key, default in self.STRING_ATTRS:
            value = metadata.get(key) or default
            if isinstance(value, six.string_types):
                value = value.strip()
            attrs[key] = value
        return attrs

    def _find_metadata(self):
        for filename in ROLE_META_FILES:
            meta_file = os.path.join(self.path, filename)
            if os.path.exists(meta_file):
                return meta_file
        return None

    def _load_metadata(self):
        meta_file = self.meta_file

        if meta_file:
            meta_file = os.path.join(self.path, meta_file)
        else:
            meta_file = self._find_metadata()

        if not meta_file:
            raise exc.ContentLoadError(
                "Failed to find metadata file. Did you forget to add "
                "'meta/main.yml' or 'meta.yml'?")

        with open(meta_file) as fp:
            metadata = yaml.safe_load(fp)

        if not isinstance(metadata, dict):
            raise exc.ContentLoadError(
                "Invalid 'meta.yml' file format, dict expected.")

        return metadata

    def _load_container_yml(self):
        container_yml = None
        container_yml_type = None

        container_meta_file = os.path.join(
            self.path, self.CONTAINER_META_FILE)
        if os.path.exists(container_meta_file):
            container_yml_type = self.CONTAINER_META_FILE
            with open(container_meta_file) as fp:
                container_yml = yaml.safe_load(fp)

        ansible_container_meta_file = os.path.join(
            self.path, self.ANSIBLE_CONTAINER_META_FILE)
        if os.path.exists(ansible_container_meta_file):
            if container_yml_type is not None:
                raise exc.ContentLoadError(
                    'Found container.yml and meta/container.yml. '
                    'A role can have only one container.yml file.')
            container_yml_type = self.ANSIBLE_CONTAINER_META_FILE
            with open(ansible_container_meta_file) as fp:
                container_yml = yaml.safe_load(fp)

        return container_yml_type, container_yml

    def _get_role_type(self, metadata, container_yml_type):
        if container_yml_type == self.CONTAINER_META_FILE:
            return constants.RoleType.CONTAINER
        if container_yml_type == self.ANSIBLE_CONTAINER_META_FILE:
            return constants.RoleType.CONTAINER_APP
        if metadata.get('demo'):
            return constants.RoleType.DEMO
        return constants.RoleType.ANSIBLE
