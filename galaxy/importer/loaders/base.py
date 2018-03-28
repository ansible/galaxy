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


class BaseLoader(object):

    content_types = None

    def __init__(self, content_type, path, logger=None):
        self.content_type = content_type
        self.path = path
        self.log = logger

        self.name = self.make_name(self.path)

    @classmethod
    def make_name(cls, path):
        """Returns content name if it can be generated from it's path.

        If name cannot be generated from the path, for example if content
        is repository-global (e.g. APB), the function should return None.

        :param str path: Content path.
        :rtype: str or None
        :return: Content name
        """
        return None


def make_module_name(path):
    return os.path.splitext(os.path.basename(path))[0]
