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

import rq.job

from django.db import models
from django.contrib.postgres import fields as psql_fields
from pulpcore.app import models as pulp_models


class Task(models.Model):
    """
    Generic table for handing tasks.

    :var params: Task parameters json dictionary
    :var result: Task result json dictionary
    """

    params = psql_fields.JSONField(null=True)
    result = psql_fields.JSONField(null=True)

    pulp_task = models.OneToOneField(
        pulp_models.Task, on_delete=models.CASCADE,
        related_name='galaxy_task'
    )

    @property
    def job_id(self):
        return self.pulp_task.job_id

    @property
    def state(self):
        return self.pulp_task.state

    @property
    def started_at(self):
        return self.pulp_task.started_at

    @property
    def finished_at(self):
        return self.pulp_task.finished_at

    @property
    def warnings(self):
        return self.pulp_task.non_fatal_errors

    @property
    def error(self):
        return self.pulp_task.error

    @classmethod
    def current(cls):
        job = rq.job.get_current_job()
        if job is None:
            raise RuntimeError(
                'This function is called outside of task context.'
            )
        return cls.objects.get(pulp_task__job_id=job.id)
