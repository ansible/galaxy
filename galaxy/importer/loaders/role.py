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
import json
import configparser

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
    linter_data = {
        'is_linter_rule_violation': True,
        'linter_type': 'importer',
        'linter_rule_id': None,
        'rule_desc': None
    }

    def __init__(self, metadata, logger=None):
        self.log = logger or base.default_logger
        self.metadata = self._get_galaxy_info(metadata)
        self.dependencies = self._get_dependencies(metadata)
        self.tox_data = None

    def _get_galaxy_info(self, metadata):
        if 'galaxy_info' in metadata:
            galaxy_info = metadata['galaxy_info']
            if not isinstance(galaxy_info, dict):
                raise exc.ContentLoadError(
                    "Expecting 'galaxy_info' in metadata to be a dictionary "
                    "or key:value mapping")
        else:
            galaxy_info = {}
        return galaxy_info

    def _get_dependencies(self, metadata):
        if 'dependencies' in metadata:
            dependencies = metadata['dependencies']
            if not isinstance(dependencies, collections.Sequence):
                raise exc.ContentLoadError(
                    "Expecting 'dependencies' in metadata to be a list")
        else:
            dependencies = []
        return dependencies

    def _validate_tag(self, tag):
        if not re.match(constants.TAG_REGEXP, tag):
            self.log.warning("Skipping invalid tag '{}'".format(tag))
            return False
        return True

    def set_tox(self, tox_data):
        self.tox_data = tox_data

    def validate_strings(self):
        required_keys = ['author', 'description', 'license']
        for key in required_keys:
            if key not in self.metadata:
                exc.ContentLoadError("Missing required key {0} in metadata"
                                     .format(key))

    def validate_license(self):
        role_license = ''
        if 'license' in self.metadata:
            role_license = self.metadata['license']

        cwd = os.path.dirname(os.path.abspath(__file__))
        license_path = os.path.join(cwd, '..', 'linters', 'spdx_licenses.json')
        license_data = json.load(open(license_path, 'r'))
        for lic in license_data['licenses']:
            if lic['licenseId'] == role_license:
                if not lic['isDeprecatedLicenseId']:
                    return
        msg = ("Expecting 'license' to be a valid SPDX license ID, "
               "instead found '%s'. "
               "For more info, visit https://spdx.org" % role_license)
        self.linter_data['linter_rule_id'] = 'invalid_license'
        self.linter_data['rule_desc'] = msg
        self.log.warning(msg, extra=self.linter_data)

    def parse_tags(self):
        tags = []

        galaxy_tags = self.metadata.get('galaxy_tags', [])
        if isinstance(galaxy_tags, list):
            tags += galaxy_tags

        if 'categories' in self.metadata:
            if isinstance(self.metadata['categories'], list):
                tags += self.metadata['categories']

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
            name = platform.get('name', None)
            if not name:
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
                msg = 'Expected item in video_links to be dictionary'
                self.linter_data['linter_rule_id'] = 'video_link_not_dict'
                self.linter_data['rule_desc'] = msg
                self.log.warning(msg, extra=self.linter_data)
                continue
            if set(video) != {'url', 'title'}:
                msg = ("Expected item in video_links to contain "
                       "only keys 'url' and 'title'")
                self.linter_data['linter_rule_id'] = 'video_link_key'
                self.linter_data['rule_desc'] = msg
                self.log.warning(msg, extra=self.linter_data)
                continue
            for name, expr in six.iteritems(self.VIDEO_REGEXP):
                match = expr.match(video['url'])
                if match:
                    file_id = match.group(1)
                    embed_url = self.VIDEO_EMBED_URLS[name].format(file_id)
                    videos.append(models.VideoLink(embed_url, video['title']))
                    break
            else:
                msg = ("URL format '{0}' is not recognized. "
                       "Expected it be a shared link from Vimeo, YouTube, "
                       "or Google Drive.".format(video['url']))
                self.linter_data['linter_rule_id'] = 'video_url_format'
                self.linter_data['rule_desc'] = msg
                self.log.warning(msg, extra=self.linter_data)
                continue
        return videos

    def check_tox(self):
        tox_tests_found = self._check_tox()
        if not tox_tests_found:
            msg = ("Molecule tests via tox not found for each stated "
                   "supported ansible version, set 'min_ansible_version'"
                   "in 'meta/main.yml' and see: "
                   "https://molecule.readthedocs.io/en/latest/ci.html#tox")
            self.linter_data['linter_rule_id'] = 'not_all_versions_tested'
            self.linter_data['rule_desc'] = msg
            self.log.warning(msg, extra=self.linter_data)
            return
        pass

    def _check_tox(self):
        SUPPORTED_MINOR_VERSIONS = ['2.5', '2.6', '2.7']

        min_ansible_version = ''
        if 'min_ansible_version' in self.metadata:
            min_ansible_version = str(self.metadata['min_ansible_version'])
        if not (min_ansible_version and self.tox_data):
            return False

        # Note: this supports a subset of the version specifiers
        # see: https://www.python.org/dev/peps/pep-0440/#version-specifiers
        try:
            deps_ansible = [d for d in self.tox_data['deps'].split('\n') if
                            d.startswith('ansible')]
            versions = [d.split(' ')[1][9:] for d in deps_ansible if
                        re.match('ansible(==|>=|~=)\d', d.split(' ')[1])]
            versions = [v.split(',')[0] for v in versions]
            tested_versions = ['.'.join(v.split('.')[:2]) for v in versions]
        except Exception:
            self.log.error('Could not parse ansible versions in tox data')
            return False

        # TODO(awcrosby): edit to support major version changes
        try:
            min_minor = '.'.join(min_ansible_version.split('.')[1])
            max_minor = '.'.join(SUPPORTED_MINOR_VERSIONS[-1].split('.')[1])
            range_of_minor = range(int(min_minor), int(max_minor) + 1)
            supported_versions = ['2.{}'.format(minor)
                                  for minor in range_of_minor]
        except Exception:
            self.log.error("Could not parse 'min_ansible_version'='{}' "
                           "to get supported versions".format(
                               min_ansible_version))
            return False

        if not (tested_versions and supported_versions):
            return False

        self.log.info("Versions supported based on "
                      "'min_ansible_version'='{}': {}".format(
                          min_ansible_version, ', '.join(supported_versions)))
        self.log.info('Stated ansible minor versions tested via '
                      'molecule in tox.ini: {}'.format(
                          ', '.join(tested_versions)))

        untested = set(supported_versions) - set(tested_versions)
        if untested:
            self.log.info('Not all supported versions tested: '
                          '{}'.format(', '.join(untested)))
            return False

        return True


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
    TOX_FILE = 'tox.ini'

    content_types = constants.ContentType.ROLE
    # temporarily removing linters.Flake8Linter
    linters = (linters.YamlLinter, linters.AnsibleLinter)

    def __init__(self, content_type, path, root, metadata_path, logger=None):
        """
        :param str path: Path to role directory within repository
        """
        super(RoleLoader, self).__init__(
            content_type, path, root, logger=logger)

        self.meta_file = metadata_path

    def load(self):
        meta_parser = self._get_meta_parser()
        galaxy_info = meta_parser.metadata
        original_name = self.name
        self.name = self._get_name(galaxy_info)

        tox_data = self._load_tox()
        meta_parser.set_tox(tox_data)

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
        meta_parser.validate_license()
        # meta_parser.check_tox()
        readme = self._get_readme()

        return models.Content(
            name=self.name,
            original_name=original_name,
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

    def _get_meta_parser(self):
        meta = self._load_metadata()
        return RoleMetaParser(meta, logger=self.log)

    def _get_name(self, galaxy_info):
        name = self.name
        if galaxy_info.get('role_name'):
            name = sanitize_content_name(galaxy_info['role_name'])
        return name

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

    def _load_tox(self):
        tox_file = os.path.join(self.path, self.TOX_FILE)

        if not os.path.exists(tox_file):
            return None

        with open(tox_file) as fp:
            config = configparser.ConfigParser()
            config.read_file(fp)
            if 'testenv' in config:
                tox_data = dict(config['testenv'])
                return tox_data
        return None

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
