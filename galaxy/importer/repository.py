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

from galaxy import constants
from galaxy.importer import loaders
from galaxy.importer import models
from galaxy.importer.utils import git
from galaxy.importer.finders import RoleFinder
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
        role = self._find_contents()
        result = list(self._load_contents(role))

        name = None
        description = None
        if result[0][0].name:
            name = result[0][0].name
        if result[0][0].description:
            description = result[0][0].description

        quality_score = self._get_repo_quality_score(result)

        return models.Repository(
            branch=branch,
            commit=commit,
            format=constants.RepositoryFormat.ROLE,
            contents=[v[0] for v in result],
            name=name,
            description=description,
            quality_score=quality_score,
        )

    def _find_contents(self):
        try:
            finder = RoleFinder(self.path, self.log)
            role = finder.find_contents()
            return role
        except exc.ContentNotFound:
            pass
        raise exc.ContentNotFound(
            'Role not found. '
            'GitHub repository import supports only a single top-level role. '
            'To import multiple contents, please follow '
            'the collection import workflow.')

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
            content.scores = loader.score()
            self.log.info(' ')

            yield content, lint_result

    def _get_repo_quality_score(self, result):
        repo_points = 0.0
        count = 0
        for content, _ in result:
            if content.scores:
                repo_points += content.scores['quality']
                count += 1
        quality_score = None if count == 0 else repo_points / count
        return quality_score
