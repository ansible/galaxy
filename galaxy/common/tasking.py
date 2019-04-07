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

import functools

from django.db import transaction
from pulpcore.app import models as pulp_models
from pulpcore.tasking.tasks import enqueue_with_reservation

from galaxy.main import models


@transaction.atomic
def create_task(
        func, params=None, options=None, resources=None,
        task_cls=models.Task, task_args=None):
    """
    Creates pulp task along with database object to store additional
    task metadata.

    :param func: Task function.
    :param params: Task parameters dictionary.
    :param options: Pulp task options.
    :param resources: Resources list to be reserved for task.
    :param task_cls: Task class.
    :param task_args: Additiona parameters for task object.

    :return: Created Task object.
    """
    resources = resources or []
    job = enqueue_with_reservation(
        func=func, resources=resources or [],
        kwargs=params, options=options)
    pulp_task = pulp_models.Task.objects.get(job_id=job.id)
    return task_cls.objects.create(
        params=params, pulp_task=pulp_task, **task_args)


def save_result(func):
    """Saves value returned by task to the database."""
    @functools.wraps
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        task = models.Task.current()
        task.result = result
        task.save()
    return wrapper
