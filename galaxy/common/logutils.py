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


class ImportTaskAdapter(logging.LoggerAdapter):
    def __init__(self, logger, task_id):
        super(ImportTaskAdapter, self).__init__(logger, {'task_id': task_id})

    def process(self, msg, kwargs):
        if self.extra:
            if 'extra' not in kwargs:
                kwargs.update({'extra': {}})
            for key, value in self.extra.items():
                kwargs['extra'][key] = value
        return msg, kwargs


class ContentTypeAdapter(logging.LoggerAdapter):
    def __init__(self, logger, content_type, content_name=None):
        super(ContentTypeAdapter, self).__init__(logger, {
            'content_type': content_type,
            'content_name': content_name,
        })

    def process(self, msg, kwargs):
        if self.extra:
            if 'extra' not in kwargs:
                kwargs.update({'extra': {}})
            for key, value in self.extra.items():
                kwargs['extra'][key] = value

        if self.extra['content_name']:
            prefix = '{}: {}'.format(
                self.extra['content_type'].name,
                self.extra['content_name'])
        else:
            prefix = self.extra['content_type']

        msg = '[{}] {}'.format(prefix, msg)
        return msg, kwargs


class ImportTaskHandler(logging.Handler):
    def emit(self, record):
        # type: (logging.LogRecord) -> None
        from galaxy.main import models
        msg = self.format(record)

        linter_keys = {'is_linter_rule_violation',
                       'linter_type',
                       'linter_rule_id',
                       'content_name'}
        if linter_keys.issubset(vars(record).keys()):
            is_linter_rule_violation = record.is_linter_rule_violation
            linter_type = record.linter_type
            linter_rule_id = record.linter_rule_id
            content_name = record.content_name
        else:
            is_linter_rule_violation = False
            linter_type = ''
            linter_rule_id = ''
            content_name = ''

        models.ImportTaskMessage.objects.using('logging').create(
            task_id=record.task_id,
            message_type=constants.ImportTaskMessageType.from_logging_level(
                record.levelno).value,
            message_text=msg,
            # content_id=5,  # TEMP think will set after creation, need name?
            is_linter_rule_violation=is_linter_rule_violation,
            linter_type=linter_type,
            linter_rule_id=linter_rule_id,
            content_name=content_name
        )
