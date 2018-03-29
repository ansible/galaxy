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
from galaxy.importer import models, lint
from galaxy.importer.utils import ast as ast_utils

from . import base


LOG = logging.getLogger(__name__)


class PluginLoader(base.BaseLoader):

    content_types = (
        constants.ContentType.ACTION_PLUGIN,
        constants.ContentType.CACHE_PLUGIN,
        constants.ContentType.CALLBACK_PLUGIN,
        constants.ContentType.CLICONF_PLUGIN,
        constants.ContentType.CONNECTION_PLUGIN,
        constants.ContentType.FILTER_PLUGIN,
        constants.ContentType.INVENTORY_PLUGIN,
        constants.ContentType.LOOKUP_PLUGIN,
        constants.ContentType.NETCONF_PLUGIN,
        constants.ContentType.SHELL_PLUGIN,
        constants.ContentType.STRATEGY_PLUGIN,
        constants.ContentType.TERMINAL_PLUGIN,
        constants.ContentType.TEST_PLUGIN,
    )
    linters = lint.Flake8Linter

    def __init__(self, content_type, path, logger=None):
        super(PluginLoader, self).__init__(content_type, path, logger=logger)

        self.documentation = None

    @classmethod
    def make_name(cls, path):
        return base.make_module_name(path)

    def load(self):
        self._parse_plugin()

        return models.Content(
            name=self.name,
            path=self.path,
            content_type=self.content_type,
            metadata={
                'documentation': self.documentation
            }
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
                    self.documentation = ast_utils.parse_ast_doc(node)
                except ValueError as e:
                    self.log.warning('Cannot parse "DOCUMENTATION": {}'
                                     .format(e))
                break
