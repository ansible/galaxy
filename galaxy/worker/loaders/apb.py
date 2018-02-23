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
import logging

import yaml

from galaxy.worker import exceptions as exc

from . import base

LOG = logging.getLogger(__name__)


class APBLoader(base.BaseLoader):
    def __init__(self, path, content_type, meta_file, name=None, logger=None):
        super(APBLoader, self).__init__(path, content_type,
                                        name=name, logger=logger)
        self.meta_file = meta_file

    def load(self):
        self.log.info('Loading metadata file: {0}'.format(self.meta_file))
        with open(os.path.join(self.path, self.meta_file)) as fp:
            metadata = yaml.safe_load(fp)

        try:
            name = metadata['name']
        except KeyError:
            raise exc.ContentLoadError('Missing "name" field in metadata')

        return base.ContentData(
            name=name,
            description=metadata.get('description'),
            content_type=self.content_type,
            metadata={
                'apb_metadata': metadata,
            },
        )
