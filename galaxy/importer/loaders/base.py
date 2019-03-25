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
from galaxy.main import models


default_logger = logging.getLogger(__name__)

BASE_SCORE = 50.0
SEVERITY_TO_WEIGHT = {
    0: 0.0,
    1: 0.75,
    2: 1.25,
    3: 2.5,
    4: 5.0,
    5: 10.0,
}
CONTENT_SEVERITY = {
    'ansible-lint_e101': 3,
    'ansible-lint_e102': 4,
    'ansible-lint_e103': 5,
    'ansible-lint_e104': 5,
    'ansible-lint_e105': 4,
    'ansible-lint_e201': 0,
    'ansible-lint_e202': 5,
    'ansible-lint_e203': 2,
    'ansible-lint_e204': 1,
    'ansible-lint_e205': 3,
    'ansible-lint_e206': 2,
    'ansible-lint_e301': 4,
    'ansible-lint_e302': 5,
    'ansible-lint_e303': 4,
    'ansible-lint_e304': 5,
    'ansible-lint_e305': 4,
    'ansible-lint_e306': 3,
    'ansible-lint_e401': 3,
    'ansible-lint_e402': 3,
    'ansible-lint_e403': 1,
    'ansible-lint_e404': 4,
    'ansible-lint_e501': 5,
    'ansible-lint_e502': 3,
    'ansible-lint_e503': 3,
    'ansible-lint_e504': 3,
    'ansible-lint_e601': 4,
    'ansible-lint_e602': 4,
    'yamllint_yaml_error': 4,
    'yamllint_yaml_warning': 1,
}
METADATA_SEVERITY = {
    'ansible-lint_e701': 4,
    'ansible-lint_e702': 4,
    'ansible-lint_e703': 4,
    'ansible-lint_e704': 2,
    'importer_importer101': 3,  # RoleImporter
    'importer_importer102': 3,  # RoleImporter
    'importer_importer103': 4,  # RoleImporter
}
COMPATIBILITY_SEVERITY = {
    'importer_not_all_versions_tested': 5,  # RoleMetaParser
}


class BaseLoader(metaclass=abc.ABCMeta):

    content_types = None
    linters = None
    can_get_scored = False

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
                    extra = {
                        'is_linter_rule_violation': True,
                        'linter_type': linter_cls.id,
                        'linter_rule_id': error_id,
                        'rule_desc': rule_desc
                    }
                    self.log.warning(message, extra=extra)
                else:
                    self.log.warning(message)
                all_linters_ok = False
            if linter_ok:
                self.log.info('{} OK.'.format(linter_obj.id))

        return all_linters_ok

    # FIXME(cutwater): Due to current object model current object limitation
    # this leads to copying README file over multiple roles.
    # We need to improve object model or add caching mechanism.
    def _get_readme(self, directory=None):
        try:
            return readmeutils.get_readme(directory or self.path, self.root)
        except readmeutils.FileSizeError as e:
            self.log.warning(e)

    def score(self):
        if not self.can_get_scored:
            return None
        task_id = self.log.logger.extra['task_id']

        import_task_messages = models.ImportTaskMessage.objects.filter(
            task_id=task_id,
            content_name=self.name,
            is_linter_rule_violation=True,
        )
        for msg in import_task_messages:
            rule_code = '{}_{}'.format(msg.linter_type,
                                       msg.linter_rule_id).lower()
            if rule_code in CONTENT_SEVERITY:
                msg.score_type = 'content'
                msg.rule_severity = CONTENT_SEVERITY[rule_code]
            elif rule_code in METADATA_SEVERITY:
                msg.score_type = 'metadata'
                msg.rule_severity = METADATA_SEVERITY[rule_code]
            elif rule_code in COMPATIBILITY_SEVERITY:
                msg.score_type = 'compatibility'
                msg.rule_severity = COMPATIBILITY_SEVERITY[rule_code]
            else:
                self.log.warning(
                    u'Severity not found for rule: {}'.format(rule_code))
                msg.is_linter_rule_violation = False
            msg.save()

        content_m = models.ImportTaskMessage.objects.filter(
            task_id=task_id,
            content_name=self.name,
            score_type='content',
            is_linter_rule_violation=True,
        )
        meta_m = models.ImportTaskMessage.objects.filter(
            task_id=task_id,
            content_name=self.name,
            score_type='metadata',
            is_linter_rule_violation=True,
        )

        content_w = [SEVERITY_TO_WEIGHT[m.rule_severity] for m in content_m]
        meta_w = [SEVERITY_TO_WEIGHT[m.rule_severity] for m in meta_m]

        scores = {}
        scores['content'] = max(0.0, (BASE_SCORE - sum(content_w)) / 10)
        scores['metadata'] = max(0.0, (BASE_SCORE - sum(meta_w)) / 10)
        scores['compatibility'] = None
        scores['quality'] = sum([scores['content'], scores['metadata']]) / 2.0

        return scores


def make_module_name(path):
    return os.path.splitext(os.path.basename(path))[0]
