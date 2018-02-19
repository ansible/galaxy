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

import logging
import os

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

    def load(self):
        return base.ContentData(
            name=self.name,
            path=self.path,
            content_type=constants.ContentType.MODULE
        )
