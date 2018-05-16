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
import pytz

from django.conf import settings
from django.db import transaction
from allauth.socialaccount import models as auth_models

from galaxy import constants
from galaxy.common import logutils
from galaxy.importer import repository as i_repo
from galaxy.importer import exceptions as i_exc
from galaxy.main import models
from galaxy.worker import exceptions as exc
from galaxy.worker import importers
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
    logger = logutils.ImportTaskAdapter(logger, task_id=import_task.id)

    try:
        _import_repository(import_task, logger)
    except exc.TaskError as e:
        import_task.finish_failed(
            reason='Task "{}" failed: {}'.format(import_task.id, str(e)))
    except Exception as e:
        LOG.exception(e)
        import_task.finish_failed(
            reason='Task "{}" failed: {}'.format(import_task.id, str(e)))
        raise


@transaction.atomic
def _import_repository(import_task, logger):
    repository = import_task.repository
    repo_full_name = repository.provider_namespace.name + "/" + repository.original_name
    logger.info(u'Starting import: task_id={}, repository={}'
                .format(import_task.id, repo_full_name))

    if import_task.repository_alt_name:
        logging.info(u'Using repository name alias: "{}"'
                     .format(import_task.repository_alt_name))
        repository.name = import_task.repository_alt_name

    if import_task.import_branch:
        repository.import_branch = import_task.import_branch

    token = _get_social_token(import_task)
    gh_api = github.Github(token)
    gh_repo = gh_api.get_repo(repo_full_name)

    try:
        repo_info = i_repo.import_repository(
            repository.clone_url,
            branch=repository.import_branch,
            temp_dir=settings.WORKER_DIR_BASE,
            logger=logger)
    except i_exc.ImporterError as e:
        raise exc.TaskError(str(e))

    context = utils.Context(
        repository=repository,
        github_token=token,
        github_client=gh_api,
        github_repo=gh_repo)

    if repository.import_branch is None:
        repository.import_branch = repo_info.branch

    new_content_objs = []
    for content_info in repo_info.contents:
        content_logger = logutils.ContentTypeAdapter(
            logger, content_info.content_type, content_info.name)
        importer_cls = importers.get_importer(content_info.content_type)
        importer = importer_cls(context, content_info, logger=content_logger)

        # TODO(cutwater): Review this code. Probably it can be improved.
        issue_tracker_url = ''
        if (hasattr(content_info, 'role_meta')
                and getattr(content_info, 'role_meta')
                and content_info.role_meta.get('issue_tracker_url')):
            issue_tracker_url = content_info.role_meta['issue_tracker_url']
        elif gh_repo.has_issues:
            issue_tracker_url = gh_repo.html_url + '/issues'
        repository.issue_tracker_url = issue_tracker_url

        content_obj = importer.do_import()

        # NOTE(cutwater): Renaming repository during import process
        # can have hidden side effects.
        if repo_info.repo_type == constants.RepositoryType.ROLE:
            repository.name = content_obj.name

        new_content_objs.append(content_obj.id)

    for obj in repository.content_objects.exclude(id__in=new_content_objs):
        logger.info(
            'Deleting Content instance: content_type={0}, '
            'namespace={1}, name={2}'.format(
                obj.content_type, obj.namespace, obj.name))
        obj.delete()

    _update_repository_versions(repository, gh_repo, logger)
    _update_namespace(gh_repo)
    _update_repository(repository, gh_repo, repo_info.commit)

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

    repository.commit = commit_info.sha
    repository.commit_message = commit_info.message[:255]
    repository.commit_url = \
        'https://api.github.com/repos/{0}/git/commits/{1}'.format(
            gh_repo.full_name, commit_info.sha)
    repository.commit_created = commit_info.committer_date
    repository.save()


def _update_repository_versions(repository, github_repo, logger):
    logger.info('Adding repo tags as versions')
    git_tag_list = github_repo.get_tags()
    for tag in git_tag_list:
        release_date = tag.commit.commit.author.date.replace(tzinfo=pytz.UTC)
        models.RepositoryVersion.objects.update_or_create(
            name=tag.name, repository=repository,
            defaults={'release_date': release_date}
        )

    if git_tag_list:
        remove_versions = []
        for version in repository.versions.all():
            found = False
            for tag in git_tag_list:
                if tag.name == version.name:
                    found = True
                    break
            if not found:
                remove_versions.append(version.name)

        if remove_versions:
            for version_name in remove_versions:
                models.RepositoryVersion.objects.filter(
                    name=version_name, repository=repository).delete()
