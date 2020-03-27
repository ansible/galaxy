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

import yaml
import configparser

from galaxy import constants
from galaxy.importer import models, linters
from galaxy.importer.loaders import base
from galaxy.importer.utils import lint as lintutils
from galaxy.importer import exceptions as exc
from galaxy.common import sanitize_content_name
from galaxy.main import models as m_models


# NOTE: ansible calls linux username which is incompatible
# with our container setup for openshift
# see: https://github.com/ansible/galaxy/issues/2303
SKIP_PARSE_DEPENDENCIES = False
try:
    from ansible.playbook.role import requirement as ansible_req
except KeyError:
    SKIP_PARSE_DEPENDENCIES = True


ROLE_META_FILES = [
    'meta/main.yml', 'meta/main.yaml',
    'meta.yml', 'meta.yaml'
]

# TODO(cutwater): Currently scoring is role specific.
#  We need to revisit this and implement generic scoring mechanism in future.

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
CONTENT_SEVERITY = {
    'ansible-lint_e101': 3,
    'ansible-lint_e102': 4,
    'ansible-lint_e103': 5,
    'ansible-lint_e104': 5,
    'ansible-lint_e105': 4,
    'ansible-lint_e201': 0,
    'ansible-lint_e202': 5,
    'ansible-lint_e203': 2,
    'ansible-lint_e204': 1,
    'ansible-lint_e205': 3,
    'ansible-lint_e206': 2,
    'ansible-lint_e301': 4,
    'ansible-lint_e302': 5,
    'ansible-lint_e303': 4,
    'ansible-lint_e304': 5,
    'ansible-lint_e305': 4,
    'ansible-lint_e306': 3,
    'ansible-lint_e401': 3,
    'ansible-lint_e402': 3,
    'ansible-lint_e403': 1,
    'ansible-lint_e404': 4,
    'ansible-lint_e501': 5,
    'ansible-lint_e502': 3,
    'ansible-lint_e503': 3,
    'ansible-lint_e504': 3,
    'ansible-lint_e601': 4,
    'ansible-lint_e602': 4,
    'yamllint_yaml_error': 4,
    'yamllint_yaml_warning': 1,
}
METADATA_SEVERITY_TYPE = 'metadata'
METADATA_SEVERITY = {
    'ansible-lint_e701': 4,
    'ansible-lint_e702': 4,
    'ansible-lint_e703': 4,
    'ansible-lint_e704': 2,
    'importer_importer101': 3,  # RoleImporter
    'importer_importer102': 3,  # RoleImporter
    'importer_importer103': 4,  # RoleImporter
}
COMPATIBILITY_SEVERITY_TYPE = 'compatibility'
COMPATIBILITY_SEVERITY = {
    'importer_not_all_versions_tested': 5,  # RoleMetaParser
}


def lookup_lint_rule(rule_code):
    """Lookup lint rule and return its type and severity.

    :param rule_code: Rule code in `<linter_type>_<code>` format.
    :return: Tuple of rule type string and severity, None if rule not found.
    """
    if rule_code in CONTENT_SEVERITY:
        return CONTENT_SEVERITY_TYPE, CONTENT_SEVERITY[rule_code]
    elif rule_code in METADATA_SEVERITY:
        return METADATA_SEVERITY_TYPE, METADATA_SEVERITY[rule_code]
    elif rule_code in COMPATIBILITY_SEVERITY:
        return COMPATIBILITY_SEVERITY_TYPE, COMPATIBILITY_SEVERITY[rule_code]
    return None


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
        if not isinstance(tag, str):
            return False
        if not re.match(constants.ROLE_TAG_REGEXP, tag):
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
        if isinstance(cloud_platforms, str):
            cloud_platforms = [cloud_platforms]
        return cloud_platforms

    # TODO: Extend dependencies support with format used
    # in .galaxy-metadata.yml
    def parse_dependencies(self):
        if SKIP_PARSE_DEPENDENCIES:
            return []
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
                continue
            if set(video) != {'url', 'title'}:
                continue
            for name, expr in self.VIDEO_REGEXP.items():
                match = expr.match(video['url'])
                if match:
                    file_id = match.group(1)
                    embed_url = self.VIDEO_EMBED_URLS[name].format(file_id)
                    videos.append(models.VideoLink(embed_url, video['title']))
                    break
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
    TOX_FILE = 'tox.ini'

    content_types = constants.ContentType.ROLE
    # temporarily removing linters.Flake8Linter
    linters = (linters.YamlLinter, linters.AnsibleLinter)

    def __init__(self, content_type, path, root, metadata_path, logger=None):
        """
        :param str path: Path to role directory within repository
        """
        super().__init__(content_type, path, root, logger=logger)

        self.meta_file = metadata_path
        self.data = {}
        self._score_stats = {}

    def load(self):
        meta_parser = self._get_meta_parser()
        galaxy_info = meta_parser.metadata
        original_name = self.name
        self.name = self._get_metadata_role_name(galaxy_info)

        tox_data = self._load_tox()
        meta_parser.set_tox(tox_data)

        meta_parser.validate_strings()

        # TODO: Refactoring required
        self.data.update(self._load_string_attrs(galaxy_info))

        container_yml_type, container_yml = self._load_container_yml()

        description = self.data.pop('description')

        self.data['role_type'] = self._get_role_type(
            galaxy_info, container_yml_type
        )
        self.data['tags'] = meta_parser.parse_tags()
        self.data['platforms'] = meta_parser.parse_platforms()
        self.data['cloud_platforms'] = meta_parser.parse_cloud_platforms()
        self.data['dependencies'] = meta_parser.parse_dependencies()
        self.data['video_links'] = meta_parser.parse_videos()
        # meta_parser.check_tox()
        readme = self._get_readme()

        self._check_tags()
        self._check_platforms()
        self._check_cloud_platforms()
        self._check_dependencies()

        return models.Content(
            name=self.name,
            original_name=original_name,
            path=self.rel_path,
            content_type=self.content_type,
            description=description,
            role_meta=self.data,
            readme=readme,
            metadata={
                'container_meta': container_yml,
            }
        )

    def score(self):
        content_w = self._score_stats.get(CONTENT_SEVERITY_TYPE, 0.0)
        content_score = max(0.0, (BASE_SCORE - content_w) / 10)

        metadata_w = self._score_stats.get(METADATA_SEVERITY_TYPE, 0.0)
        metadata_score = max(0.0, (BASE_SCORE - metadata_w) / 10)

        return {
            'content': content_score,
            'metadata': metadata_score,
            'compatibility': None,
            'quality': sum([content_score, metadata_score]) / 2.0
        }

    def make_name(self):
        if self.rel_path:
            return os.path.basename(self.path)
        else:
            return None

    def _on_lint_issue(self, linter_type, rule_id, rule_desc, message=None):
        lint_record = lintutils.LintRecord(linter_type, rule_id, rule_desc)
        rule_code = '{}_{}'.format(linter_type, rule_id).lower()
        rule_info = lookup_lint_rule(rule_code)

        if rule_info is not None:
            lint_record.score_type = rule_info[0]
            lint_record.severity = rule_info[1]

            self._score_stats[lint_record.score_type] = (
                self._score_stats.get(lint_record.score_type, 0.0)
                + SEVERITY_TO_WEIGHT[lint_record.severity])
        else:
            self.log.warning(
                'Severity not found for rule: {}'.format(rule_code))
        self.log.warning(message or rule_desc,
                         extra={'lint_record': lint_record})

    def _get_meta_parser(self):
        meta = self._load_metadata()
        return RoleMetaParser(meta, logger=self.log)

    def _get_metadata_role_name(self, galaxy_info):
        """Get role_name from repository role metadata, if it exists.

        Collections do not support role_name.
        Collections have self.name already set via directory path.
        """

        name = self.name
        is_collection = bool(self.name)

        if is_collection:
            if galaxy_info.get('role_name'):
                self.log.warning("Role in collection gets name from directory,"
                                 " ignoring the 'role_name' attribute")
            return name

        if galaxy_info.get('role_name'):
            name = sanitize_content_name(galaxy_info['role_name'])
        return name

    def _load_string_attrs(self, metadata):
        attrs = {}
        for key, default in self.STRING_ATTRS:
            value = metadata.get(key) or default
            if isinstance(value, str):
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

    def _check_tags(self):
        self.log.info('Checking role metadata tags')
        tags = self.data['tags'] or []
        if tags and len(tags) > constants.MAX_TAGS_COUNT:
            self.log.warning(
                'Found more than {0} galaxy tags in metadata. '
                'Only first {0} will be used'
                .format(constants.MAX_TAGS_COUNT))
            self.data['tags'] = tags[:constants.MAX_TAGS_COUNT]

    def _check_platforms(self):
        self.log.info('Checking role platforms')
        confirmed_platforms = []

        for platform in self.data['platforms']:
            name = platform.name
            versions = platform.versions
            if 'all' in versions:
                platform_objs = m_models.Platform.objects.filter(
                    name__iexact=name
                )
                if not platform_objs:
                    msg = u'Invalid platform: "{}-all", skipping.'.format(name)
                    self._on_lint_issue('importer', 'IMPORTER101', msg)
                    continue
                for p in platform_objs:
                    confirmed_platforms.append(p)
                continue

            for version in versions:
                try:
                    p = m_models.Platform.objects.get(
                        name__iexact=name, release__iexact=str(version)
                    )
                except m_models.Platform.DoesNotExist:
                    msg = (u'Invalid platform: "{0}-{1}", skipping.'
                           .format(name, version))
                    self._on_lint_issue('importer', 'IMPORTER101', msg)
                else:
                    confirmed_platforms.append(p)

        self.data['platforms'] = confirmed_platforms

    def _check_cloud_platforms(self):
        self.log.info('Checking role cloud platforms')
        confirmed_platforms = []

        for name in self.data['cloud_platforms']:
            try:
                c = m_models.CloudPlatform.objects.get(name__iexact=name)
            except m_models.CloudPlatform.DoesNotExist:
                msg = u'Invalid cloud platform: "{0}", skipping'.format(name)
                self._on_lint_issue('importer', 'IMPORTER102', msg)
            else:
                confirmed_platforms.append(c)

        self.data['cloud_platforms'] = confirmed_platforms

    def _check_dependencies(self):
        self.log.info('Checking role dependencies')
        confirmed_deps = []

        for dep in self.data['dependencies'] or []:
            try:
                dep_role = m_models.Content.objects.get(
                    namespace__name=dep.namespace, name=dep.name)
                confirmed_deps.append(dep_role)
            except Exception:
                msg = u"Error loading dependency: '{}'".format(
                    '.'.join([d for d in dep]))
                self._on_lint_issue('importer', 'IMPORTER103', msg)

        self.data['dependencies'] = confirmed_deps
