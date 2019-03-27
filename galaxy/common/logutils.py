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
from galaxy.importer.utils import lint as lintutils


class BaseLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {}).update(self.extra)
        return msg, kwargs


class ImportTaskAdapter(BaseLoggerAdapter):
    def __init__(self, logger, task_id):
        super(ImportTaskAdapter, self).__init__(logger, {'task_id': task_id})


class ContentTypeAdapter(BaseLoggerAdapter):
    def __init__(self, logger, content_type, content_name=None):
        super(ContentTypeAdapter, self).__init__(logger, {
            'content_type': content_type,
            'content_name': content_name,
        })


class ImportTaskHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        from galaxy.main import models

        create_kwargs = {}

        lint_record: lintutils.LintRecord = getattr(
            record, 'lint_record', None)
        if lint_record:
            create_kwargs = {
                'is_linter_rule_violation': True,
                'linter_type': lint_record.type,
                'linter_rule_id': lint_record.code,
                'rule_desc': lint_record.message,
                'rule_severity': lint_record.severity,
                'score_type': lint_record.score_type,
                'content_name': record.content_name,
            }

        # TODO(cutwater): Revisit connection alias usage.
        models.ImportTaskMessage.objects.using('logging').create(
            task_id=record.task_id,
            message_type=constants.ImportTaskMessageType.from_logging_level(
                record.levelno).value,
            message_text=record.msg,
            **create_kwargs,
        )
