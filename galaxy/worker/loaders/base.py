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

import abc
import logging

import six

LOG = logging.getLogger(__name__)


class ContentData(object):

    _fields = frozenset([
        'name',
        'path',
        'content_type',
        'description',
        'dependencies',
        'metadata',
    ])

    def __init__(self, **kwargs):
        kwargs.setdefault('metadata', {})

        for k in self._fields:
            v = kwargs.pop(k, None)
            setattr(self, k, v)

        if kwargs:
            raise ValueError('Invalid fields: "{0}"'.format(kwargs.keys()))


@six.add_metaclass(abc.ABCMeta)
class BaseLoader(object):

    def __init__(self, path, logger=None):
        self.path = path
        self.log = logger or LOG

    @abc.abstractmethod
    def load(self):
        pass
