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

import datetime
import logging

import celery
import github
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from allauth.socialaccount.models import SocialToken

from galaxy.main.models import (Content,
                                ImportTask,
                                ProviderNamespace)
from galaxy.main import models
from galaxy.main import constants

from galaxy.main.celerytasks.elastic_tasks import update_custom_indexes
from galaxy.worker import exceptions as exc
from galaxy.worker import loaders
from galaxy.worker import importers
from galaxy.worker import utils
from galaxy.worker import logging as wlog

LOG = logging.getLogger(__name__)


def update_user_repos(github_repos, user):
    """
    Refresh user repositories. Used by refresh_user_repos task and
    galaxy.api.views.RefreshUserRepos.
    Returns user.repositories.all() queryset.
    """
    LOG.info("Starting update_user_repos for user {0}"
             .format(user.username))
    new_repos = set()
    for repo in github_repos:
        if repo.private:
            continue

        LOG.info("Create or Update repo {0}".format(repo.full_name))
        repo_user, repo_name = repo.full_name.split('/')
        provider_ns = models.ProviderNamespace.objects.get(
            provider__name=constants.PROVIDER_GITHUB,
            name=repo_user,
        )
        db_repo, created = models.Repository.objects.get_or_create(
            provider_namespace=provider_ns, name=repo_name,
            defaults={'is_enabled': False,
                      'original_name': repo_name})
        user.repositories.add(db_repo)
        if not created:
            cnt = models.Content.objects.filter(repository=db_repo).count()
            db_repo.enabled = cnt > 0
            db_repo.save()
        new_repos.add(repo.full_name)

    # Remove any that are no longer present in GitHub
    for repo in user.repositories.all():
        repo_name = "{0}/{1}".format(repo.provider_namespace.name, repo.name)
        if repo_name not in new_repos:
            LOG.info("Remove from cache {0}".format(repo_name))
            user.repositories.remove(repo)

    LOG.info("Finished update_user_repos for user {0}"
             .format(user.username))


def refresh_existing_user_repos(token, github_user):
    """
    Remove repos belonging to the user that are no longer accessible in GitHub,
    or update github_user, github_repo, if it has changed.
    """
    LOG.info("Starting refresh_existing_user_repos for GitHub user {0}"
             .format(github_user.login))
    gh_api = github.Github(token)

    for db_repo in models.Repository.objects.filter(
            provider_namespace__name=github_user.login):
        old_name = "{0}/{1}".format(db_repo.github_user, db_repo.github_repo)
        try:
            gh_repo = gh_api.get_repo(old_name, lazy=False)
        except github.UnknownObjectException:
            LOG.info(u'Repository not found, deleting: {0}'
                     .format(old_name))
            db_repo.delete()
            continue

        try:
            new_name = '{0}/{1}'.format(gh_repo.owner.login, gh_repo.name)
            if old_name.lower() != new_name.lower():
                LOG.info(u'UPDATED: {0} to {1}'.format(old_name, new_name))
                provider_ns = models.ProviderNamespace.objects.get(
                    provider=constants.PROVIDER_GITHUB,
                    name=github_user,
                )
                db_repo.provider_namespace = provider_ns
                db_repo.name = gh_repo.name
                db_repo.save()
        except Exception as e:
            LOG.error(u"Error: refresh_existing_user_repos {0} - {1}"
                      .format(old_name, e.message))
    LOG.info("Finished refresh_existing_user_repos for GitHub user {0}"
             .format(github_user.login))


def _update_namespace(repo):
    # Use GitHub repo to update namespace attributes
    if repo.owner.type == 'Organization':
        owner = repo.organization
    else:
        owner = repo.owner

    ProviderNamespace.objects.update_or_create(
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
        token = SocialToken.objects.get(
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
        github_repo=gh_repo,
    )
    repo_loader = loaders.RepositoryLoader.from_remote(
        remote_url=import_task.repository.clone_url,
        clone_dir=workdir,
        name=repository.original_name,
        logger=logger)

    new_content_objs = []

    for loader in repo_loader.load():
        assert isinstance(loader, loaders.RoleLoader)

        importer = importers.RoleImporter(context, loader)
        role = importer.import_content()
        new_content_objs.append(role.id)
        update_custom_indexes.delay(
            username=role.namespace, tags=role.get_tags(),
            platforms=role.get_unique_platforms(),
            cloud_platforms=role.get_cloud_platforms())

    for obj in repository.content_objects.exclude(id__in=new_content_objs):
        logger.info(
            'Deleting Content instance: content_type={0}, '
            'namespace={1}, name={2}'.format(
                obj.content_type, obj.namespace, obj.name))
        obj.delete()

    _update_namespace(gh_repo)
    _update_repository(repository, gh_repo, repo_loader.last_commit_info)

    import_task.finish_success(u'Import completed')


@celery.task(name="galaxy.main.celerytasks.tasks.import_repository")
def import_repository(task_id):
    LOG.info(u"Starting task: %d" % int(task_id))

    try:
        import_task = ImportTask.objects.get(id=task_id)
    except ImportTask.DoesNotExist:
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


@celery.task(name="galaxy.main.celerytasks.tasks.refresh_user_repos",
             throws=(Exception,))
@transaction.atomic
def refresh_user_repos(user, token):
    LOG.info(u"Refreshing User Repo Cache for {}".format(user.username))

    try:
        gh_api = github.Github(token)
    except github.GithubException as exc:
        user.cache_refreshed = True
        user.save()
        msg = u"User {} Repo Cache Refresh Error: {}".format(
            user.username, unicode(exc))
        LOG.error(msg)
        raise Exception(msg)

    try:
        ghu = gh_api.get_user()
    except github.GithubException as exc:
        user.cache_refreshed = True
        user.save()
        msg = u"User {} Repo Cache Refresh Error: {}".format(
            user.username, unicode(exc))
        LOG.error(msg)
        raise Exception(msg)

    try:
        repos = ghu.get_repos()
    except github.GithubException as exc:
        user.cache_refreshed = True
        user.save()
        msg = u"User {} Repo Cache Refresh Error: {}".foramt(
            user.username, unicode(exc))
        LOG.error(msg)
        raise Exception(msg)

    refresh_existing_user_repos(token, ghu)

    update_user_repos(repos, user)
    user.github_avatar = ghu.avatar_url
    user.github_user = ghu.login
    user.cache_refreshed = True
    user.save()


@celery.task(name="galaxy.main.celerytasks.tasks.refresh_user_stars",
             throws=(Exception,))
@transaction.atomic
def refresh_user_stars(user, token):
    LOG.info(u"Refreshing User Stars for {}".format(user.username))

    try:
        gh_api = github.Github(token)
    except github.GithubException as exc:
        msg = u"User {} Refresh Stars: {}".format(user.username, unicode(exc))
        LOG.error(msg)
        raise Exception(msg)

    try:
        ghu = gh_api.get_user()
    except github.GithubException as exc:
        msg = u"User {} Refresh Stars: {}".format(user.username, unicode(exc))
        LOG.error(msg)
        raise Exception(msg)

    try:
        subscriptions = ghu.get_subscriptions()
    except github.GithubException as exc:
        msg = u"User {} Refresh Stars: {}".format(user.username, unicode(exc))
        LOG.error(msg)
        raise Exception(msg)

    # Refresh user subscriptions class
    user.subscriptions.all().delete()
    for s in subscriptions:
        name = s.full_name.split('/')
        cnt = Content.objects.filter(
            repository__provider_namespace__name=name[0],
            repository__name=name[1]).count()
        if cnt > 0:
            user.subscriptions.get_or_create(
                github_user=name[0],
                github_repo=name[1],
                defaults={
                    'github_user': name[0],
                    'github_repo': name[1]
                })

    try:
        starred = ghu.get_starred()
    except github.GithubException as exc:
        msg = u"User {0} Refresh Stars: {1}".format(user.username, unicode(exc))
        LOG.error(msg)
        raise Exception(msg)

    new_starred = {(s.owner.login, s.name) for s in starred}
    old_starred = {(s.repository.github_user, s.repository.github_repo): s.id
                   for s in user.starred.select_related('repository').all()}

    to_remove = [v for k, v in old_starred.iteritems()
                 if k not in new_starred]
    to_add = new_starred - set(old_starred)

    user.starred.filter(id__in=to_remove).delete()

    for github_user, github_repo in to_add:
        try:
            role = Content.objects.get(
                repository__provider_namespace__name=github_user,
                repository__name=github_repo)
        except Content.DoesNotExist:
            continue
        user.starred.create(role=role)


@celery.task(name="galaxy.main.celerytasks.tasks.refresh_role_counts")
def refresh_role_counts(start, end, token, tracker):
    '''
    Update each role with latest counts from GitHub
    '''
    tracker.state = 'RUNNING'
    tracker.save()

    passed = 0
    failed = 0
    deleted = 0
    updated = 0
    gh_api = github.Github(token)
    for role in Content.objects.filter(is_valid=True, active=True,
                                       id__gt=start, id__lte=end):
        full_name = "%s/%s" % (role.github_user, role.github_repo)
        try:
            repo = gh_api.get_repo(full_name, lazy=False)
        except github.UnknownObjectException:
            LOG.error(u"NOT FOUND: {0}".format(full_name))
            role.delete()
            deleted += 1
            continue

        try:
            repo_name = repo.name
            repo_owner = repo.owner.login
            if (role.github_repo.lower() != repo_name.lower()
                    or role.github_user.lower() != repo_owner.lower()):
                updated += 1
                LOG.info(u'UPDATED: {0} to {1}/{2}'.format(
                    full_name, repo_owner, repo_name
                ))
                role.github_user = repo_owner
                role.github_repo = repo_name
                role.save()
            else:
                passed += 1
        except Exception as exc:
            LOG.error(u"FAILED: {0} - {1}".format(full_name, unicode(exc)))
            failed += 1

    tracker.state = 'FINISHED'
    tracker.passed = passed
    tracker.failed = failed
    tracker.deleted = deleted
    tracker.updated = updated
    tracker.save()


# ----------------------------------------------------------------------
# Periodic Tasks
# ----------------------------------------------------------------------

@celery.task(name="galaxy.main.celerytasks.tasks.clear_stuck_imports")
def clear_stuck_imports():
    one_hours_ago = timezone.now() - datetime.timedelta(seconds=3600)
    LOG.info(u"Clear Stuck Imports: {}".format(
        one_hours_ago.strftime("%Y-%m-%d %H:%M:%S")).encode('utf-8').strip())
    try:
        for ri in ImportTask.objects.filter(
                created__lte=one_hours_ago,
                state__in=[ImportTask.STATE_PENDING,
                           ImportTask.STATE_RUNNING]):
            LOG.info(u"Clear Stuck Imports: {0} - {1}.{2}"
                     .format(ri.id, ri.repository.github_repo,
                             ri.repository.github_user))
            ri.state = u"FAILED"
            ri.messages.create(
                message_type=u"ERROR",
                message_text=(
                    u'Import timed out, please try again. If you continue '
                    u'seeing this message you may '
                    u'have a syntax error in your "meta/main.yml" file.')
            )
            ri.save()
            transaction.commit()
    except Exception as exc:
        LOG.error(u"Clear Stuck Imports ERROR: {}".format(unicode(exc)))
        raise
