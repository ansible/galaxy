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

import glob
import logging
import os
import subprocess

import yaml

from galaxy.main import constants
from galaxy.worker import utils
from galaxy.worker import exceptions as exc
from galaxy.worker import loaders


LOG = logging.getLogger(__name__)


class RepositoryLoader(object):
    APB_META_FILES = ['apb.yml', 'apb.yaml']
    REPO_META_FILENAME = '.ansible-galaxy.yml'

    # NOTE(cutwater): APBLoader should not be included in this list,
    # because APB is a single-content repository and cannot be nested
    # into repository along with other content types.
    REPO_LOADERS = [
        ('roles', loaders.RoleLoader,
         constants.ContentType.ROLE),
        ('library', loaders.ModuleLoader,
         constants.ContentType.MODULE),
        ('action_plugins', loaders.PluginLoader,
         constants.ContentType.ACTION_PLUGIN),
        ('cache_plugins', loaders.PluginLoader,
         constants.ContentType.CACHE_PLUGIN),
        ('callback_plugins', loaders.PluginLoader,
         constants.ContentType.CALLBACK_PLUGIN),
        ('cliconf_plugins', loaders.PluginLoader,
         constants.ContentType.CLICONF_PLUGIN),
        ('connection_plugins', loaders.PluginLoader,
         constants.ContentType.CONNECTION_PLUGIN),
        ('filter_plugins', loaders.PluginLoader,
         constants.ContentType.FILTER_PLUGIN),
        ('inventory_plugins', loaders.PluginLoader,
         constants.ContentType.INVENTORY_PLUGIN),
        ('lookup_plugins', loaders.PluginLoader,
         constants.ContentType.LOOKUP_PLUGIN),
        ('netconf_plugins', loaders.PluginLoader,
         constants.ContentType.NETCONF_PLUGIN),
        ('shell_plugins', loaders.PluginLoader,
         constants.ContentType.SHELL_PLUGIN),
        ('strategy_plugins', loaders.PluginLoader,
         constants.ContentType.STRATEGY_PLUGIN),
        ('terminal_plugins', loaders.PluginLoader,
         constants.ContentType.TERMINAL_PLUGIN),
        ('test_plugins', loaders.PluginLoader,
         constants.ContentType.TEST_PLUGIN),
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
        :param str name: Repository name.
        :param logging.Logger: Logger instance.
        """
        self.path = path
        self.name = name
        self.metadata = None
        self.log = logger or LOG

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
            loaders_ = finder()
            if loaders_:
                return loaders_
        raise exc.ContentLoadError(
            "Cannot load content from repository.")

    def _try_load_apb(self):
        self.log.debug('Content search - Looking for apb.yml')
        for meta_file in self.APB_META_FILES:
            meta_path = os.path.join(self.path, meta_file)
            if not os.path.exists(meta_path):
                continue
            return [loaders.APBLoader(
                self.path, constants.ContentType.APB, meta_file=meta_file,
                name=self.name, logger=self.log)]
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

        loaders_ = []
        for name, content_type, loader_cls in self.REPO_LOADERS:
            for content in self.metadata[name]:
                path = content['path'].rstrip('/')
                for path in glob.glob(path):
                    loaders_.append(loader_cls(
                        path=path, content_type=content_type, logger=self.log))
        return loaders_

    def _find_toplevel_role(self):
        self.log.debug('Content search - Looking for top level role '
                       'metadata file')
        for meta_file in loaders.ROLE_META_FILES:
            if os.path.exists(os.path.join(self.path, meta_file)):
                return [loaders.RoleLoader(
                    path=self.path, content_type=constants.ContentType.ROLE,
                    name=self.name, meta_file=meta_file, logger=self.log
                )]
        return None

    def _find_from_repository(self):
        self.log.debug('Content search - Analyzing repository structure')
        loaders_ = []
        for directory, loader_cls, content_type in self.REPO_LOADERS:
            path = os.path.join(self.path, directory)
            if not os.path.exists(path):
                continue
            self.log.debug('Found directory "{}"'.format(directory))
            loaders_.extend(loader_cls.find_content(
                path, content_type, logger=self.log))
        return loaders_
