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
import os

import six

from galaxy.common import logutils


default_logger = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseLoader(object):

    content_types = None
    linters = None

    def __init__(self, content_type, path, root, logger=None):
        """
        :param content_type: Content type.
        :param path: Path to content file or directory relative to
            repository root.
        :param root: Repository root path.
        :param logger: Optional logger instance.
        """
        self.content_type = content_type
        self.rel_path = path
        self.root = root
        self.name = self.make_name()

        self.log = logutils.ContentTypeAdapter(
            logger or default_logger, self.content_type, self.name)

    @property
    def path(self):
        return os.path.join(self.root, self.rel_path)

    def make_name(self):
        """Returns content name if it can be generated from it's path.

        If name cannot be generated from the path, for example if content
        is repository-global (e.g. APB), the function should return None.

        :param str path: Content path.
        :rtype: str or None
        :return: Content name
        """
        return None

    @abc.abstractmethod
    def load(self):
        pass

    def lint(self):
        if not self.linters:
            return
        self.log.info('Linting...')

        linters = self.linters
        if not isinstance(linters, (list, tuple)):
            linters = [linters]

        ok = True
        for linter_cls in linters:
            for message in linter_cls(self.root).check_files(self.rel_path):
                self.log.error(message)
                ok = False

        if ok:
            self.log.info('Linting OK.')
        return ok


def make_module_name(path):
    return os.path.splitext(os.path.basename(path))[0]
