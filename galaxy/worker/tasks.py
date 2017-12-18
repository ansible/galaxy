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

import celery
from django.conf import settings

from galaxy.main import models
from galaxy.worker import utils
from galaxy.worker import loaders


LOG = logging.getLogger(__name__)


def _update_role_videos(role, videos):
    # type: (models.Content, [loaders.role.VideoLink]) -> None
    role.videos.all().delete()
    for video in videos:
        role.videos.create(
            url=video['url'],
            description=video['title'])


def _update_platforms(role, platforms):
    # type: (models.Content, [loaders.role.PlatformInfo]) -> None
    old_platforms = {(p.name, p.release): p for p in role.platforms.all()}
    new_platforms = {}
    for platform in platforms:
        if 'all' in platform.versions:
            db_platforms = models.Platform.objects.filter(name=platform.name)
            new_platforms.update({
                (platform.name, p.release): p for p in db_platforms})
        else:
            for version in platform.versions:
                try:
                    p = models.Platform.objects.get(
                        name=platform.name, release=version)
                except models.Platform.DoesNotExist:
                    LOG.warn("Invalid platform: {0}-{1}, skipping".format(
                        platform.name, version))
                    continue
                new_platforms[(platform.name, version)] = p

    for p in set(new_platforms) - set(old_platforms):
        role.platforms.add(new_platforms[p])

    for p in set(old_platforms) - set(new_platforms):
        role.platforms.delete(old_platforms[p])


def _update_role_metadata(role, data):
    # type: (models.Content, loaders.RoleData) -> None
    raw_attrs = (
        'author'
        'company',
        'description',
        'min_ansible_version',
        'min_ansible_container_version',
        'issue_tracker_url',
    )
    for attr in raw_attrs:
        setattr(role, attr, getattr(data, attr))
    _update_role_videos(role, data.video_links)
    _update_platforms(role, data.platforms)
    # _update_cloud_platforms(role, data.cloud_platforms)


def _update_content(obj, data):
    # type: (models.Content, loaders.RoleData) -> None
    if isinstance(data, loaders.RoleData):
        _update_role_metadata(obj, data)


def _import_repository(task):
    basedir = settings.WORKER_DIR_BASE
    with utils.TemporaryDirectory(dir=basedir) as workdir:
        utils.clone_repository(task.repository.clone_url, workdir)

        loader = loaders.RepositoryLoader(workdir)
        loader.load()
        for data in loader.load_contents():
            obj = models.Content.objects.get_or_create(
                repository=task.repository,
                content_type=models.ContentType.get(data.content_type),
                name=data.name,
            )
            _update_content(obj, data)


@celery.task
def import_repository(task_id):
    task = models.ImportTask.objects.get(id=task_id)
    task.start()

    try:
        _import_repository(task)
    except Exception as e:
        task.finish_failed(e)
        LOG.exception(e)
        raise
