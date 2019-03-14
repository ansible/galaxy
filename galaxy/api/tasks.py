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

# FIXME(cutwater): This module is deprecated. It should be moved
#   to `galaxy.api.v1` package and eventually removed.
from galaxy.main import models
from galaxy.worker import tasks as worker_tasks


def create_import_task(
        repository, user, import_branch=None, travis_status_url='',
        travis_build_url='', user_initiated=False):

    # if no import_branch specified, use repo import_branch
    import_branch = import_branch or repository.import_branch

    task = models.ImportTask.objects.create(
        repository=repository,
        owner=user,
        import_branch=import_branch,
        travis_status_url=travis_status_url,
        travis_build_url=travis_build_url,
        state=models.ImportTask.STATE_PENDING
    )
    worker_tasks.import_repository.delay(
        task.id,
        user_initiated=user_initiated
    )
    return task
