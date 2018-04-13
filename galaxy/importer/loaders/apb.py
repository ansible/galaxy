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

import yaml

from galaxy import constants
from galaxy.importer import exceptions as exc
from galaxy.importer.loaders import base


class APBLoader(base.BaseLoader):
    content_type = constants.ContentType.APB

    def __init__(self, content_type, path, root, metadata_file, logger=None):
        super(APBLoader, self).__init__(
            content_type, root, path, logger=logger)
        self.metadata_file = metadata_file

    def load(self):
        self.log.info('Loading metadata file: {0}'.format(self.metadata_file))
        with open(os.path.join(self.path, self.metadata_file)) as fp:
            metadata = yaml.safe_load(fp)

        try:
            name = metadata['name']
        except KeyError:
            raise exc.ContentLoadError('Missing "name" field in metadata')

        return dict(
            name=name,
            content_type=self.content_type,
            description=metadata.get('description'),
            metadata={
                'apb_metadata': metadata,
            },
        )
