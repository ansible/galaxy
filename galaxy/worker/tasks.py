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
import github

from django.conf import settings
from django.db import transaction
from allauth.socialaccount import models as auth_models

from galaxy.main.celerytasks import elastic_tasks
from galaxy.main import constants
from galaxy.main import models
from galaxy.worker import exceptions as exc
from galaxy.worker import importers
from galaxy.worker import logging as wlog
from galaxy.worker import repository as repo
from galaxy.worker import utils


LOG = logging.getLogger(__name__)


@celery.task
def import_repository(task_id):
    LOG.info(u"Starting task: %d" % int(task_id))

    try:
        import_task = models.ImportTask.objects.get(id=task_id)
    except models.ImportTask.DoesNotExist:
        LOG.error(u"Failed to get task id: %d" % int(task_id))
        raise

    import_task.start()

    logger = logging.getLogger('galaxy.worker.tasks.import_repository')
    logger = wlog.ImportTaskAdapter(logger, task_id=import_task.id)

    try:
        with utils.WorkerCloneDir(settings.WORKER_DIR_BASE) as workdir:
            _import_repository(import_task, workdir, logger)
    except Exception as e:
        LOG.exception(e)
        import_task.finish_failed(
            reason='Task "{}" failed: {}'.format(import_task.id, str(e)))
        raise


@transaction.atomic
def _import_repository(import_task, workdir, logger):
    repository = import_task.repository
    repo_full_name = repository.github_user + "/" + repository.github_repo
    logger.info(u'Starting import: task_id={}, repository={}'
                .format(import_task.id, repo_full_name))

    if import_task.repository_alt_name:
        logging.info(u'Using repository name alias: "{}"'
                     .format(import_task.repository_alt_name))
        repository.name = import_task.repository_alt_name

    token = _get_social_token(import_task)
    gh_api = github.Github(token)
    gh_repo = gh_api.get_repo(repo_full_name)

    context = utils.Context(
        workdir=workdir,
        repository=repository,
        github_token=token,
        github_client=gh_api,
        github_repo=gh_repo)
    repo_loader = repo.RepositoryLoader.from_remote(
        remote_url=import_task.repository.clone_url,
        clone_dir=workdir,
        name=repository.original_name,
        logger=logger)

    new_content_objs = []

    for loader in repo_loader.load():
        data = loader.load()

        importer_cls = importers.get_importer(data.content_type)
        importer = importer_cls(context, data, logger=loader.log)
        content = importer.do_import()

        new_content_objs.append(content.id)

        # TODO(cutwater): Move to RoleImporter class
        elastic_tasks.update_custom_indexes.delay(
            username=content.namespace, tags=content.get_tags(),
            platforms=content.get_unique_platforms(),
            cloud_platforms=content.get_cloud_platforms())

    for obj in repository.content_objects.exclude(id__in=new_content_objs):
        logger.info(
            'Deleting Content instance: content_type={0}, '
            'namespace={1}, name={2}'.format(
                obj.content_type, obj.namespace, obj.name))
        obj.delete()

    _update_namespace(gh_repo)
    _update_repository(repository, gh_repo, repo_loader.last_commit_info)

    import_task.finish_success(u'Import completed')


def _update_namespace(repository):
    # Use GitHub repo to update namespace attributes
    if repository.owner.type == 'Organization':
        owner = repository.organization
    else:
        owner = repository.owner

    models.ProviderNamespace.objects.update_or_create(
        provider__name=constants.PROVIDER_GITHUB,
        name=owner.login,
        defaults={
            'display_name': owner.name,
            'avatar_url': owner.avatar_url,
            'location': owner.location,
            'company': owner.company,
            'email': owner.email,
            'html_url': owner.html_url,
            'followers': owner.followers
        })


def _get_social_token(import_task):
    user = import_task.owner
    try:
        token = auth_models.SocialToken.objects.get(
            account__user=user, account__provider='github')
        return token.token
    except Exception:
        raise exc.TaskError(
            u"Failed to get GitHub account for Galaxy user {0}. "
            u"You must first authenticate with GitHub.".format(user.username))


def _update_repository(repository, gh_repo, commit_info):
    repository.stargazers_count = gh_repo.stargazers_count
    repository.watchers_count = gh_repo.subscribers_count
    repository.forks_count = gh_repo.forks_count
    repository.open_issues_count = gh_repo.open_issues_count

    repository.commit = commit_info['sha']
    repository.commit_message = commit_info['message'][:255]
    repository.commit_url = \
        'https://api.github.com/repos/{0}/git/commits/{1}'.format(
            gh_repo.full_name, commit_info['sha'])
    repository.commit_created = commit_info['committer_date']
    repository.save()
