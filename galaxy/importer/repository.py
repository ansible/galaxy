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

import logging

from galaxy import constants
from galaxy.importer import loaders
from galaxy.importer import models
from galaxy.importer.utils import git
from galaxy.importer.utils import readme as readmeutils
from galaxy.importer import finders as finders_
from galaxy.importer import exceptions as exc


default_logger = logging.getLogger(__name__)


def import_repository(url, branch=None, temp_dir=None, logger=None):
    with git.make_clone_dir(temp_dir) as clone_dir:
        try:
            git.clone_repository(url, clone_dir, branch=branch)
        except Exception as e:
            raise exc.RepositoryError(e)
        return load_repository(clone_dir, logger)


def load_repository(directory, logger=None):
    """
    :param directory: Repository directory path.
    :type logger: logging.Logger
    :param logger: Optional logger instance.
    """
    logger = logger or default_logger
    return RepositoryLoader(directory, logger=logger).load()


class RepositoryLoader(object):
    """Loads repository and content info."""

    finders = [
        # finders_.MetadataFinder,
        finders_.ApbFinder,
        finders_.RoleFinder,
        finders_.FileSystemFinder,
    ]

    def __init__(self, path, name=None, logger=None):
        """
        :param str path: Path to the repository directory.
        :param str name: Repository name.
        :param logging.Logger: Logger instance.
        """
        self.path = path
        self.name = name
        self.metadata = None
        self.log = logger or default_logger

    def load(self):
        branch = git.get_current_branch(directory=self.path)
        commit = git.get_commit_info(directory=self.path)
        finder, contents = self._find_contents()
        result = list(self._load_contents(contents))
        readme = self._get_readme(finder.repository_format)
        description = None

        name = None
        if finder.repository_format in (constants.RepositoryFormat.ROLE,
                                        constants.RepositoryFormat.APB):
            if result[0][0].name:
                name = result[0][0].name
            if result[0][0].description:
                description = result[0][0].description

        return models.Repository(
            branch=branch,
            commit=commit,
            format=finder.repository_format,
            contents=[v[0] for v in result],
            readme=readme,
            name=name,
            description=description
        )

    def _find_contents(self):
        for finder_cls in self.finders:
            try:
                finder = finder_cls(self.path, self.log)
                contents = finder.find_contents()
                return finder, contents
            except exc.ContentNotFound:
                pass
        raise exc.ContentNotFound("No content found in repository")

    def _load_contents(self, contents):
        for content_type, rel_path, extra in contents:
            loader_cls = loaders.get_loader(content_type)
            loader = loader_cls(content_type, rel_path, self.path,
                                logger=self.log, **extra)

            self.log.info('===== LOADING {} ====='.format(
                          content_type.name))
            content = loader.load()
            self.log.info(' ')

            name = ': {}'.format(content.name) if content.name else ''
            self.log.info('===== LINTING {}{} ====='.format(
                          content_type.name, name))
            lint_result = loader.lint()
            self.log.info(' ')
            yield content, lint_result

    def _get_readme(self, repository_format):
        if repository_format == constants.RepositoryFormat.MULTI:
            try:
                return readmeutils.get_readme(directory=self.path)
            except readmeutils.FileSizeError as e:
                self.log.warning(e)
        return None
