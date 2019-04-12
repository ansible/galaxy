# (c) 2012-2019, Ansible by Red Hat
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

import uuid

from django.utils import timezone
from pulpcore import constants as pulp_const
from pulpcore.app import models as pulp_models

from galaxy.main import models
from galaxy.api.v2 import serializers


class TestBaseTaskSerializer:

    def test_serialize(self):
        job_id = uuid.uuid4()
        now = timezone.now()
        pulp_task = pulp_models.Task(
            pk=24,
            job_id=job_id,
            state=pulp_const.TASK_STATES.WAITING,
            started_at=now,
            finished_at=None,
        )
        instance = models.Task(
            id=42,
            pulp_task=pulp_task
        )

        serializer = serializers.BaseTaskSerializer(instance)

        # NOTE(cutwater): If settings.USE_TZ is set django timezone.now()
        #   returns aware datetime object with tzinfo set to UTC.
        #   At the same time Rest framework DateTimeSerializer converts is
        #   to local timezone.
        #   Probably we should use UTC for everything.
        assert serializer.data == {
            'id': 42,
            'job_id': str(job_id),
            'state': 'waiting',
            'started_at': timezone.localtime(now).isoformat(),
            'finished_at': None,
            'error': None,
        }
