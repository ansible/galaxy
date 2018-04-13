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

from galaxy import constants
from galaxy.importer import linters
from galaxy.importer import models
from galaxy.importer.loaders import base


class ModuleUtilsLoader(base.BaseLoader):

    content_types = constants.ContentType.MODULE_UTILS
    linters = linters.Flake8Linter

    def __init__(self, content_type, path, root, logger=None):
        super(ModuleUtilsLoader, self).__init__(
            content_type, path, root, logger=logger)

    def make_name(self):
        return base.make_module_name(self.path)

    def load(self):
        return models.Content(
            name=self.name,
            path=self.rel_path,
            content_type=self.content_type,
        )
