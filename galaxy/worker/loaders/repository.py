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

import glob
import logging
import os
import subprocess

import yaml

from galaxy.worker import utils
from galaxy.worker import exceptions as exc
from galaxy.worker.loaders import role as role_loader
from galaxy.worker.loaders import apb as apb_loader


LOG = logging.getLogger(__name__)


class RepositoryLoader(object):
    APB_META_FILES = ['apb.yml', 'apb.yaml']
    REPO_META_FILENAME = '.ansible-galaxy.yml'

    # NOTE(cutwater): APBLoader should not be included in this list,
    # because APB is a single-content repository and cannot be nested
    # into repository along with other content types.
    REPO_LOADERS = [
        ('roles', role_loader.RoleLoader)
    ]
    GIT_LOG_FORMAT_FIELDS = [
        ('sha', '%H'),
        ('author_name', '%an'),
        ('author_email', '%ae'),
        ('author_date', '%ad'),
        ('committer_name', '%cn'),
        ('committer_email', '%ce'),
        ('committer_date', '%cd'),
        ('message', '%B'),
    ]

    def __init__(self, path, name=None, logger=None):
        """
        :param str path: Path to the repository directory.
        """
        self.path = path
        self.name = name
        self.metadata = None
        self.log = logger or None

        self._current_branch = None
        self._last_commit = None
        self._last_commit_info = None

    # TODO(cutwater): Use @cached_property
    @property
    def last_commit(self):
        if self._last_commit is None:
            cmd = ['git', 'rev-parse', 'HEAD']
            self._last_commit = subprocess.check_output(
                cmd, cwd=self.path).strip()
        return self._last_commit

    @property
    def last_commit_info(self):
        if self._last_commit_info is None:
            info = utils.get_commit_info(
                fields=self.GIT_LOG_FORMAT_FIELDS,
                directory=self.path, date_format='raw')
            info['author_date'] = utils.parse_git_date_raw(
                info['author_date'])
            info['committer_date'] = utils.parse_git_date_raw(
                info['committer_date'])
            self._last_commit_info = info
        return self._last_commit_info

    @property
    def current_branch(self):
        if self._current_branch is None:
            cmd = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
            self._current_branch = subprocess.check_output(
                cmd, cwd=self.path).strip()
        return self._current_branch

    @classmethod
    def from_remote(cls, remote_url, clone_dir, name, branch=None, logger=None):
        utils.clone_repository(
            remote_url, directory=clone_dir, branch=branch)
        return cls(path=clone_dir, name=name, logger=logger)

    def load(self):
        for finder in [self._find_from_metadata,
                       self._try_load_apb,
                       self._find_toplevel_role,
                       self._find_from_repository]:
            loaders = finder()
            if loaders:
                return loaders
        raise exc.ContentLoadError(
            "Cannot load content from repository.")

    def _try_load_apb(self):
        self.log.debug('Content search - Looking for apb.yml')
        for filename in self.APB_META_FILES:
            metadata_file = os.path.join(self.path, filename)
            if os.path.exists(metadata_file):
                return [apb_loader.APBLoader(
                    self.path, self.name, filename, logger=self.log)]
        return None

    def _find_from_metadata(self):
        self.log.debug('Content search - Looking for {0}'
                       .format(self.REPO_META_FILENAME))
        metadata_file = os.path.join(self.path, self.REPO_META_FILENAME)
        if not os.path.exists(metadata_file):
            self.log.debug('Content search - File {0} not found'
                           .format(self.REPO_META_FILENAME))
            return None
        with open(metadata_file) as fp:
            self.metadata = yaml.safe_load(fp)

        loaders = []
        for name, loader_cls in self.REPO_LOADERS:
            for content in self.metadata[name]:
                path = content['path'].rstrip('/')
                for path in glob.glob(path):
                    loaders.append(loader_cls(path, logger=self.log))
        return loaders

    def _find_toplevel_role(self):
        self.log.debug('Content search - Looking for top level role '
                       'metadata file')
        for meta_file in role_loader.ROLE_META_FILES:
            if os.path.exists(os.path.join(self.path, meta_file)):
                return [role_loader.RoleLoader(
                    path=self.path, name=self.name,
                    meta_file=meta_file,
                    logger=self.log
                )]
        return None

    def _find_from_repository(self):
        self.log.debug('Content search - Analyzing repository structure')
        loaders = []
        for loader_name, loader_cls in self.REPO_LOADERS:
            contents_path = os.path.join(self.path, loader_name)
            if not os.path.exists(contents_path):
                continue
            loaders.extend(loader_cls.find_content(
                contents_path, logger=self.log))
        return loaders
