# (c) 2012-2016, Ansible by Red Hat
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

from __future__ import print_function

import time
import logging

from math import ceil, floor

from django.conf import settings
from django.db.models import Max, Q
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from galaxy.accounts.models import CustomUser as User
from galaxy.main.models import Role, RefreshRoleCount
from galaxy.worker.tasks import refresh_role_counts
from allauth.socialaccount.models import SocialToken


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        u"Update each role's GitHub stargazer and watcher counts, "
        u"and remove any roles that no longer exist on GitHub."
    )

    def handle(self, *args, **options):

        # Users should already be authenticated to Galaxy via GitHub
        # and have a valid token.
        task_users = []
        for task_user in settings.GITHUB_TASK_USERS:
            try:
                user = User.objects.get(username=task_user)
            except ObjectDoesNotExist:
                logger.info(u"USER NOT FOUND: {0}".format(task_user))
                continue
            try:
                token = SocialToken.objects.get(
                    account__user=user, account__provider='github'
                )
            except ObjectDoesNotExist:
                logger.info(
                    u"GITHUB TOKEN NOT FOUND: for user {0}".format(task_user)
                )
                continue
            task_users.append({
                u'username': task_user,
                u'token': token.token
            })

        if len(task_users) == 0:
            raise Exception(
                u"No task workers found with valid GitHub tokens. "
                u"Make sure your task workers are configured properly."
            )

        agg = Role.objects.filter(
            is_valid=True, active=True).aggregate(Max('id'))
        max_id = agg['id__max']
        size = ceil(max_id / float(len(settings.GITHUB_TASK_USERS)))
        in_list = []

        logger.info(u"Refresh Role Counts")
        for i in range(len(task_users)):
            start = size * i
            end = size * (i + 1)
            logger.info(
                u"User: {} Range: {} - {}"
                .format(task_users[i]['username'], start, end)
            )
            role_count = RefreshRoleCount.objects.create(
                state='PENDING',
                description=(
                    'User: {} Range: {}-{}'
                    .format(task_users[i]['username'], start, end)
                )
            )
            in_list.append(role_count.id)
            refresh_role_counts.delay(
                start, end, task_users[i]['token'], role_count
            )

        logger.info(u"Requests submitted to Celery. "
                    u"Waiting for task completion...")
        finished = False
        started = time.time()
        while not finished:
            finished = True
            for obj in RefreshRoleCount.objects.filter(
                    Q(pk__in=in_list), ~Q(state='COMPLETED')):
                if not obj.state == 'FINISHED':
                    finished = False
                else:
                    print(
                        u"{0} Total: {1} Passed: {2} Failed: {3} "
                        u"Deleted: {4} Updated: {5}"
                        .format(
                            obj.description,
                            (obj.failed + obj.passed
                             + obj.deleted + obj.updated),
                            obj.passed,
                            obj.failed,
                            obj.deleted,
                            obj.updated
                        )
                    )
                    obj.state = 'COMPLETED'
                    obj.save()
            time.sleep(60)

        elapsed = time.time() - started
        hours = floor(elapsed / 3600) if elapsed >= 3600 else 0
        minutes = (
            floor((elapsed - (hours * 3600)) / 60)
            if (elapsed - (hours * 3600)) >= 60
            else 0
        )
        seconds = elapsed - (hours * 3600) - (minutes * 60)
        logger.info(
            u"Elapsed time {0:0=2d}.{0:0=2d}.{0:0=2d}"
            .format(hours, minutes, seconds)
        )
