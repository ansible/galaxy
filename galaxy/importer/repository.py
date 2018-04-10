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

from galaxy.importer import loaders
from galaxy.importer import models
from galaxy.importer.utils import git
from galaxy.importer import finders as finders_
from galaxy.importer import exceptions as exc

LOG = logging.getLogger(__name__)


def import_repository(url, branch=None, temp_dir=None, logger=None):
    with git.make_clone_dir(temp_dir) as clone_dir:
        git.clone_repository(url, clone_dir, branch=branch)
        return load_repository(clone_dir, logger)


def load_repository(directory, logger=None):
    """
    :param directory: Repository directory path.
    :type logger: logging.Logger
    :param logger: Optional logger instance.
    """
    logger = logger or LOG
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
        self.log = logger or LOG

    def load(self):
        branch = git.get_current_branch(directory=self.path)
        commit = git.get_commit_info(directory=self.path)
        result = list(self._get_contents())

        # if not all(v[1] for v in result):
        #     raise exc.ContentLoadError('Lint failed')

        return models.Repository(
            branch=branch,
            commit=commit,
            contents=[v[0] for v in result],
        )

    def _find_contents(self):
        for finder in self.finders:
            try:
                return finder(self.path, self.log).find_contents()
            except exc.ContentNotFound:
                pass
        raise exc.ContentNotFound("No content found in repository")

    def _get_contents(self):
        for content_type, rel_path, extra in self._find_contents():
            loader_cls = loaders.get_loader(content_type)
            loader = loader_cls(content_type, rel_path, self.path,
                                logger=self.log, **extra)
            content = loader.load()
            lint_result = loader.lint()
            yield content, lint_result
