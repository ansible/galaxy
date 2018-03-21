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

import collections
import glob
import itertools
import logging
import os

from galaxy import constants
from galaxy.importer import exceptions as exc


LOG = logging.getLogger(__name__)

ROLE_META_FILES = [
    'meta/main.yml', 'meta/main.yaml',
    'meta.yml', 'meta.yaml'
]

Result = collections.namedtuple(
    'Result', ['content_type', 'path', 'extra'])


class BaseFinder(object):

    def __init__(self, path, logger=None):
        self.path = path
        self.log = logger or LOG

    def find_contents(self):
        """Finds contents in path and return the results.

        :rtype: Iterator[Result]
        :return: Iterator of find results.
        """
        raise NotImplementedError


class ApbFinder(BaseFinder):
    """Searches for APB repository."""
    META_FILES = ['apb.yml', 'apb.yaml']

    def find_contents(self):
        self.log.debug('Content search - Looking for file "apb.yml"')
        meta_path = _find_metadata(self.path, self.META_FILES)
        if meta_path:
            meta_path = os.path.join(self.path, meta_path)
            return [Result(constants.ContentType.APB, self.path,
                           extra={'metadata_path': meta_path})]
        raise exc.ContentNotFound


class RoleFinder(BaseFinder):
    """Searches for a repository global role."""
    def find_contents(self):
        self.log.debug(
            'Content search - Looking for top level role metadata file')
        meta_path = _find_metadata(self.path, ROLE_META_FILES)
        if meta_path:
            meta_path = os.path.join(self.path, meta_path)
            return [Result(constants.ContentType.ROLE, self.path,
                           extra={'metadata_path': meta_path})]
        raise exc.ContentNotFound


class FileSystemFinder(BaseFinder):
    """Searches for content in repository top level directories."""

    def find_contents(self):
        self.log.debug('Content search - Analyzing repository structure')
        content = self._find_content()
        # Check if finder has found at least one content
        try:
            first = next(content)
        except StopIteration:
            raise exc.ContentNotFound
        else:
            return itertools.chain([first], content)

    def _find_content(self):
        for content_type, directory, func in self._content_type_dirs():
            content_path = os.path.join(self.path, directory)
            if not os.path.exists(content_path):
                continue
            for content in func(content_type, content_path):
                yield content

    def _find_modules(self, content_type, content_path):
        content_dirs = (
            [content_path]
            + glob.glob(content_path + '/*')
            + glob.glob(content_path + '/*/*'))
        content_dirs = filter(os.path.isdir, content_dirs)

        for dir_ in content_dirs:
            for file_path in glob.glob(dir_ + '/*.py'):
                file_name = os.path.basename(file_path)
                if not os.path.isfile(file_path) or file_name == '__init__.py':
                    continue
                yield Result(content_type, file_path, extra={})

    @staticmethod
    def _find_roles(content_type, content_path):
        for name in os.listdir(content_path):
            path = os.path.join(content_path, name)
            if not os.path.isdir(path):
                continue
            meta_path = _find_metadata(path, ROLE_META_FILES)
            if not meta_path:
                continue
            yield Result(content_type, path,
                         extra={'metadata_path': meta_path})

    def _find_module_utils(self, content_type, content_path):
        return [Result(content_type, content_path, extra={})]

    def _content_type_dirs(self):
        for content_type in constants.ContentType:
            if content_type == constants.ContentType.ROLE:
                yield content_type, 'roles', self._find_roles
            elif content_type == constants.ContentType.MODULE:
                yield content_type, 'library', self._find_modules
            # FIXME(cutwater): Add module_utils type
            elif content_type.value.endswith('_plugin'):
                yield (content_type, content_type.value + 's',
                       self._find_modules)


class MetadataFinder(BaseFinder):
    """Searches for content defined in galaxy-metadata.yaml file."""

    def find_contents(self):
        raise NotImplementedError


def _find_metadata(path, files):
    """Finds metadata file in specified path.

    :param str path: Lookup path
    :param [str] files: List of file names.
    :rtype: str or None
    :returns: File relative name if it is found, None otherwise.
    """
    for file_ in files:
        meta_path = os.path.join(path, file_)
        if os.path.exists(meta_path):
            return file_
    return None
