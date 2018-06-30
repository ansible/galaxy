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
import collections
import itertools
import logging
import os

import six

from galaxy import constants
from galaxy.importer import exceptions as exc


default_logger = logging.getLogger(__name__)

ROLE_META_FILES = [
    'meta/main.yml', 'meta/main.yaml',
    'meta.yml', 'meta.yaml'
]

Result = collections.namedtuple(
    'Result', ['content_type', 'path', 'extra'])


@six.add_metaclass(abc.ABCMeta)
class BaseFinder(object):

    def __init__(self, path, logger=None):
        self.path = path
        self.log = logger or default_logger

    @abc.abstractproperty
    def repository_format(self):
        pass

    @abc.abstractmethod
    def find_contents(self):
        """Finds contents in path and return the results.

        :rtype: Iterator[Result]
        :return: Iterator of find results.
        """
        pass


class ApbFinder(BaseFinder):
    """Searches for APB repository."""
    META_FILES = ['apb.yml', 'apb.yaml']

    repository_format = constants.RepositoryFormat.APB

    def find_contents(self):
        self.log.debug('Content search - Looking for file "apb.yml"')
        meta_path = _find_metadata(self.path, self.META_FILES)
        if meta_path:
            meta_path = os.path.join(self.path, meta_path)
            return [Result(constants.ContentType.APB, '',
                           extra={'metadata_path': meta_path})]
        raise exc.ContentNotFound


class RoleFinder(BaseFinder):
    """Searches for a repository global role."""

    repository_format = constants.RepositoryFormat.ROLE

    def find_contents(self):
        self.log.debug(
            'Content search - Looking for top level role metadata file')
        meta_path = _find_metadata(self.path, ROLE_META_FILES)
        if meta_path:
            meta_path = os.path.join(self.path, meta_path)
            return [Result(constants.ContentType.ROLE, '',
                           extra={'metadata_path': meta_path})]
        raise exc.ContentNotFound


class FileSystemFinder(BaseFinder):
    """Searches for content in repository top level directories."""

    repository_format = constants.RepositoryFormat.MULTI

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
            # TODO(cutwater): Use `yield from` after migration to Python 3
            for content in func(content_type, content_path):
                yield content

    def _find_modules(self, content_type, content_dir):
        for file_name in os.listdir(content_dir):
            file_path = os.path.join(content_dir, file_name)
            if os.path.isdir(file_path):
                self.log.warning("Directory detected: '{0}'. "
                                 "Nested modules are not supported.")
                continue
            if (not os.path.isfile(file_path)
                    or not file_name.endswith('.py')
                    or file_name == '__init__.py'):
                continue
            rel_path = os.path.relpath(file_path, self.path)
            yield Result(content_type, rel_path, extra={})

    def _find_roles(self, content_type, content_dir):
        for dir_name in os.listdir(content_dir):
            file_path = os.path.join(content_dir, dir_name)
            if not os.path.isdir(file_path):
                continue
            meta_path = _find_metadata(file_path, ROLE_META_FILES)
            if not meta_path:
                continue
            rel_path = os.path.relpath(file_path, self.path)
            yield Result(content_type, rel_path,
                         extra={'metadata_path': meta_path})

    def _content_type_dirs(self):
        yield constants.ContentType.ROLE, 'roles', self._find_roles

        # NOTE(cutwater): All directories except `rolese` are disabled
        # in accordance to https://github.com/ansible/galaxy/issues/571
        # for content_type in constants.ContentType:
        #     if content_type == constants.ContentType.ROLE:
        #         yield content_type, 'roles', self._find_roles
        #     elif content_type == constants.ContentType.MODULE:
        #         yield content_type, 'library', self._find_modules
        #     elif content_type == constants.ContentType.MODULE_UTILS:
        #         yield content_type, 'module_utils', self._find_modules
        #     elif content_type.value.endswith('_plugin'):
        #         yield (content_type, content_type.value + 's',
        #                self._find_modules)


class MetadataFinder(BaseFinder):
    """Searches for content defined in galaxy-metadata.yaml file."""

    repository_format = constants.RepositoryFormat.MULTI

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
