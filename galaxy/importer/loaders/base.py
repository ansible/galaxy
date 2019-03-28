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

from galaxy.common import logutils
from galaxy.importer.utils import readme as readmeutils
from galaxy.importer.utils import lint as lintutils


default_logger = logging.getLogger(__name__)


class BaseLoader(metaclass=abc.ABCMeta):
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

        linters = self.linters
        if not isinstance(linters, (list, tuple)):
            linters = [linters]

        all_linters_ok = True
        for linter_cls in linters:
            linter_ok = True
            linter_obj = linter_cls(self.root)
            for message in linter_obj.check_files(self.rel_path):
                if linter_ok:
                    self.log.info('{} Warnings:'.format(linter_obj.id))
                    linter_ok = False
                error_id, rule_desc = linter_obj.parse_id_and_desc(message)
                if error_id:
                    self._on_lint_issue(
                        linter_cls.id, error_id, rule_desc, message)
                else:
                    self.log.warning(message)
                all_linters_ok = False
            if linter_ok:
                self.log.info('{} OK.'.format(linter_obj.id))

        return all_linters_ok

    def score(self):
        return None

    def _on_lint_issue(self, linter_type, rule_id, rule_desc, message=None):
        lint_record = lintutils.LintRecord(linter_type, rule_id, rule_desc)
        self.log.warning(message or rule_desc,
                         extra={'lint_record': lint_record})

    # FIXME(cutwater): Due to current object model current object limitation
    # this leads to copying README file over multiple roles.
    # We need to improve object model or add caching mechanism.
    def _get_readme(self, directory=None):
        try:
            return readmeutils.get_readme(directory or self.path, self.root)
        except readmeutils.FileSizeError as e:
            self.log.warning(e)


def make_module_name(path):
    return os.path.splitext(os.path.basename(path))[0]
