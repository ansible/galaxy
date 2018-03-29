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

from galaxy import constants
from galaxy.importer import lint
from galaxy.importer import models
from galaxy.importer.utils import ast as ast_utils
from galaxy.importer.loaders import base

LOG = logging.getLogger(__name__)


class ModuleLoader(base.BaseLoader):

    content_types = constants.ContentType.MODULE
    linters = lint.Flake8Linter

    def __init__(self, content_type, path, logger=None):
        super(ModuleLoader, self).__init__(content_type, path, logger=logger)

        self.documentation = None
        self.metdata = None

    @classmethod
    def make_name(cls, path):
        return base.make_module_name(path)

    def load(self):
        self._parse_module()

        description = ''
        if self.documentation:
            description = self.documentation.get('short_description', '')

        return models.Content(
            name=self.name,
            path=self.path,
            content_type=self.content_type,
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
                try:
                    self.documentation = ast_utils.parse_ast_doc(node)
                except ValueError as e:
                    self.log.warning('Cannot parse "DOCUMENTATION": {}'
                                     .format(e))

    def _parse_metdata(self, node):
        # type (ast.Dict) -> dict
        if not isinstance(node.value, ast.Dict):
            self.log.warning('Cannot parse "ANSIBLE_METADATA" field, '
                             'dict expected')
            return

        return ast.literal_eval(node.value)
