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

import yaml

from . import base
from . import common


LOG = logging.getLogger(__name__)


class PluginLoader(base.PythonModuleLoader):

    def __init__(self, path, content_type, name=None, logger=None):
        super(PluginLoader, self).__init__(path, content_type,
                                           name=name, logger=logger)
        self.documentation = None

    def load(self):
        self._parse_plugin()

        return base.ContentData(
            name=self.name,
            path=self.path,
            content_type=self.content_type
        )

    def _parse_plugin(self):
        with open(self.path) as fp:
            code = fp.read()

        module = ast.parse(code)  # type: ast.Module
        assert isinstance(module, ast.Module), 'Module expected'

        for node in module.body:
            if not isinstance(node, ast.Assign):
                continue

            name = node.targets[0].id

            if name == 'DOCUMENTATION':
                try:
                    self.documentation = common.parse_ast_doc(node)
                except ValueError as e:
                    self.log.warning('Cannot parse "DOCUMENTATION": {}'
                                     .format(e))
                break

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
