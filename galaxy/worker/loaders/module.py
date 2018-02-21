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

import ast
import logging
import os

import yaml

from galaxy.main import constants
from galaxy.worker import logging as wlog

from . import base


LOG = logging.getLogger(__name__)


class ModuleLoader(base.FileContentMixin, base.BaseLoader):

    def __init__(self, path, logger=None):
        name = os.path.basename(path)
        if not os.path.isdir(path):
            name, _ = os.path.splitext(name)
        logger = wlog.ContentTypeAdapter(logger or LOG, 'Module', name)

        super(ModuleLoader, self).__init__(path, logger)

        self.name = name

        self.documentation = None
        self.metdata = None

    def load(self):

        self._parse_module()

        description = ''
        if self.documentation:
            description = self.documentation.get('short_description', '')

        return base.ContentData(
            name=self.name,
            path=self.path,
            content_type=constants.ContentType.MODULE,
            description=description,
            metadata={
                'ansible_metadata': self.metdata,
                'documentation': self.documentation
            }
        )

    def _parse_module(self):
        with open(self.path) as fp:
            code = fp.read()

        module = ast.parse(code)  # type: ast.Module
        assert isinstance(module, ast.Module), 'Module expected'

        for node in module.body:
            if not isinstance(node, ast.Assign):
                continue

            name = node.targets[0].id

            if name == 'ANSIBLE_METADATA':
                self.metadata = self._parse_metdata(node)
            elif name == 'DOCUMENTATION':
                self.documentation = self._parse_doc(node)

    def _parse_metdata(self, node):
        # type (ast.Dict) -> dict
        if not isinstance(node.value, ast.Dict):
            self.log.warning('Cannot parse "ANSIBLE_METADATA" field, '
                             'dict expected')
            return

        return ast.literal_eval(node.value)

    def _parse_doc(self, node):
        # type (ast.Str) -> dict
        if not isinstance(node.value, ast.Str):
            self.log.warning('Cannot parse "DOCUMENTATION" field, '
                             'string expected')
            return
        try:
            documentation = yaml.safe_load(node.value.s)
        except yaml.YAMLError as e:
            self.log.warning('Cannot parse "DOCUMENTATION" field: {}'
                             .format(e))
            return

        if not isinstance(documentation, dict):
            self.log.warning('Invalid "DOCUMENTATION" value, YAML document'
                             'should be a dictionary')
        return documentation
