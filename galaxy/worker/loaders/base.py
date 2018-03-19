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

from __future__ import absolute_import

import abc
import glob
import logging
import os

import six

from galaxy.worker import logging as wlog

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

    def __init__(self, path, content_type, name=None, logger=None):
        self.path = path
        self.content_type = content_type
        self.name = name or self.get_name()
        self.log = wlog.ContentTypeAdapter(
            logger or LOG, content_type, self.name)

    @abc.abstractmethod
    def load(self):
        pass

    def get_name(self):
        return None

    @classmethod
    def find_content(cls, content_path, content_type, logger=None):
        raise TypeError('This loader cannot find content')


class PythonModuleLoader(BaseLoader):
    """Finds content (modules, plugins) provided by python modules"""
    @classmethod
    def find_content(cls, content_path, content_type, logger=None):
        for dir_ in cls._get_dirs(content_path):
            for file_path in glob.glob(dir_ + '/*.py'):
                file_name = os.path.basename(file_path)
                if not os.path.isfile(file_path) or file_name == '__init__.py':
                    continue
                yield cls(path=file_path, content_type=content_type,
                          logger=logger)

    def get_name(self):
        return os.path.splitext(os.path.basename(self.path))[0]

    @staticmethod
    def _get_dirs(content_path):
        content_dirs = (
            [content_path]
            + glob.glob(content_path + '/*')
            + glob.glob(content_path + '/*/*'))
        return filter(os.path.isdir, content_dirs)


class DirectoryLoader(BaseLoader):
    """Finds content (e.g. roles) provided by directories"""
    @classmethod
    def find_content(cls, content_path, content_type, logger=None):
        for name in os.listdir(content_path):
            path = os.path.join(content_path, name)
            if not os.path.isdir(path):
                continue
            yield cls(path=path, content_type=content_type, logger=logger)

    def get_name(self):
        return os.path.basename(self.path)
