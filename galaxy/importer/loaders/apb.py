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

import os
import re
import yaml

from galaxy import constants
from galaxy.importer import exceptions as exc
from galaxy.importer import linters
from galaxy.importer import models
from galaxy.importer.loaders import base


class APBMetaParser(object):
    # Tags should contain lowercase letters and digits only
    TAG_REGEXP = re.compile('^[a-z0-9]+$')
    VERSIONS = ['1.0']

    def __init__(self, metadata, logger=None):
        self.metadata = metadata
        self.log = logger or base.default_logger

    def check_data(self):
        self._check_version()
        self._check_async()
        self._check_bindable()
        self._check_metadata()
        self._check_plans()

    def _get_key(self, key):
        try:
            value = self.metadata[key]
        except KeyError:
            raise exc.APBContentLoadError(
                'Missing "{0}" field in metadata.'.format(key))
        return value

    def _check_version(self):
        version = self._get_key('version')
        try:
            version_string = '{:.1f}'.format(version)
        except ValueError:
            raise exc.APBContentLoadError(
                'Version "{0}" in metadata is an invalid version '
                'format'.format(version))
        if version_string not in self.VERSIONS:
            raise exc.APBContentLoadError(
                'Version "{0}" in metadata is not a valid version of '
                'the APB spec'.format(version_string))

    def _check_bindable(self):
        fieldname = 'bindable'
        value = self._get_key(fieldname)
        if not isinstance(value, bool):
            raise exc.APBContentLoadError(
                'Expecting "{0}" in metadata to be a boolean '
                'value'.format(fieldname))

    def _check_for_keys(self, keys, fieldname, data):
        for key in keys:
            try:
                data[key]
            except KeyError:
                self.log.warning(
                    'Key "{0}" not defined in "{1}" of '
                    'metadata'.format(key, fieldname))

    def _check_metadata(self):
        fieldname = 'metadata'
        meta = self._get_key(fieldname)
        if not isinstance(meta, dict):
            raise exc.APBContentLoadError(
                'Expecting "{0}" in metadata to be a dictionary '
                'or key:value mapping'.format(fieldname))
        expected_keys = (
            'documentationUrl', 'imageUrl', 'dependencies',
            'displayName', 'longDescription', 'providerDisplayName')
        self._check_for_keys(expected_keys, fieldname, meta)

    def _check_plans(self):
        fieldname = 'plans'
        plans = self._get_key(fieldname)
        if not isinstance(plans, list):
            raise exc.APBContentLoadError(
                'Expecting "plans" in metadata to be a list')

        expected_plan_keys = ('description', 'free', 'metadata', 'parameters')
        expected_plan_meta_keys = ('displayName', 'longDescription', 'cost')
        expected_parameter_keys = ('name', 'title', 'type')
        idx = 0
        for plan in plans:
            if not isinstance(plan, dict):
                raise exc.APBContentLoadError(
                    'Expecting "plans" in metadata to be a list of '
                    'dictionaries or key:value mappings')
            try:
                plan['name']
            except KeyError:
                raise exc.APBContentLoadError(
                    'Expecting "name" to be defined for each plan found in '
                    'metadata.')
            self._check_for_keys(expected_plan_keys,
                                 'plans[{0}]'.format(idx), plan)
            if plan.get('metadata'):
                self._check_for_keys(expected_plan_meta_keys,
                                     'plans[{0}].metadata'.format(idx),
                                     plan['metadata'])
            if plan.get('parameters'):
                if not isinstance(plan['parameters'], list):
                    raise exc.APBContentLoadError(
                        'Expecting "parameters" in "plans[{0}]" of metadata to '
                        'be a list'.format(idx))
                pidx = 0
                for params in plan['parameters']:
                    if not isinstance(params, dict):
                        raise exc.APBContentLoadError(
                            'Expecting "parameters[{0}]" in "plans[{1}]" of '
                            'metadata to be a dictionary or mapping of '
                            'key:value pairs'.format(idx, pidx))
                    self._check_for_keys(
                        expected_parameter_keys,
                        'plans[{0}].parameters[{1}]'.format(idx, pidx),
                        params)
                    pidx += 1
            idx += 1

    def _check_async(self):
        fieldname = 'async'
        value = self._get_key(fieldname)
        if value not in ('optional', 'required', 'unsupported'):
            raise exc.APBContentLoadError(
                'Expecting "{0}" in metadata to be one of "optional", '
                '"required", "unsupported"'.format(fieldname))

    def parse_name(self):
        fieldname = 'name'
        name = self._get_key(fieldname)
        if not re.match('^[a-z0-9_.-]+$', name):
            raise exc.APBContentLoadError(
                'Invalid "{0}" value in metadata. Must contain only lowercase '
                'letters, digits, underscore, period and dash'.format(fieldname))
        return name

    def parse_description(self):
        return self._get_key('description')

    def _validate_tag(self, tag):
        if not re.match(self.TAG_REGEXP, tag):
            self.log.warning(
                '"{0}" is not a valid tag in metadata. Skipping.'.format(tag))
            return False
        return True

    def parse_tags(self):
        tags = []
        apb_tags = self.metadata.get('tags', [])
        if isinstance(apb_tags, list):
            tags += apb_tags
        else:
            self.log.warning('Expected "tags" in metadata to be a list')
        tags = list(filter(self._validate_tag, tags))
        return tags


class APBLoader(base.BaseLoader):
    content_types = constants.ContentType.APB
    linters = (linters.YamlLinter,)

    def __init__(self, content_type, path, root, metadata_path, logger=None):
        super(APBLoader, self).__init__(content_type, path, root, logger=logger)
        self.metadata_file = metadata_path

    def load(self):
        self.log.info('Loading metadata file: {0}'.format(self.metadata_file))
        metadata = self._load_metadata()
        meta_parser = APBMetaParser(metadata, logger=self.log)
        name = meta_parser.parse_name()
        description = meta_parser.parse_description()
        meta_parser.check_data()
        data = {}
        data['tags'] = meta_parser.parse_tags()

        return models.Content(
            name=name,
            path=self.rel_path,
            content_type=self.content_type,
            description=description,
            role_meta=data,
            metadata={
                'apb_metadata': metadata,
            },
        )

    def _load_metadata(self):
        with open(os.path.join(self.path, self.metadata_file)) as fp:
            metadata = yaml.safe_load(fp)
        if not isinstance(metadata, dict):
            raise exc.ContentLoadError(
                "Invalid 'apb.yml' file format, dict expected.")
        return metadata
