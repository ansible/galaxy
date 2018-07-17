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

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from galaxy.main.models import (Content,
                                ImportTask)
from galaxy.main import models
from galaxy import constants

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
        try:
            provider_ns = models.ProviderNamespace.objects.get(
                provider__name=constants.PROVIDER_GITHUB,
                name=repo_user,
            )
        except ObjectDoesNotExist:
            continue
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
            user.username, exc)
        LOG.error(msg)
        raise Exception(msg)

    try:
        ghu = gh_api.get_user()
    except github.GithubException as exc:
        user.cache_refreshed = True
        user.save()
        msg = u"User {} Repo Cache Refresh Error: {}".format(
            user.username, exc)
        LOG.error(msg)
        raise Exception(msg)

    try:
        repos = ghu.get_repos()
    except github.GithubException as exc:
        user.cache_refreshed = True
        user.save()
        msg = u"User {} Repo Cache Refresh Error: {}".foramt(
            user.username, exc)
        LOG.error(msg)
        raise Exception(msg)

    refresh_existing_user_repos(token, ghu)

    update_user_repos(repos, user)
    user.avatar_url = ghu.avatar_url
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
        msg = u"User {} Refresh Stars: {}".format(user.username, exc)
        LOG.error(msg)
        raise Exception(msg)

    try:
        ghu = gh_api.get_user()
    except github.GithubException as exc:
        msg = u"User {} Refresh Stars: {}".format(user.username, exc)
        LOG.error(msg)
        raise Exception(msg)

    try:
        subscriptions = ghu.get_subscriptions()
    except github.GithubException as exc:
        msg = u"User {} Refresh Stars: {}".format(user.username, exc)
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
        msg = u"User {0} Refresh Stars: {1}".format(user.username, exc)
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
    """
    Update each role with latest counts from GitHub
    """
    tracker.state = 'RUNNING'
    tracker.save()

    passed = 0
    failed = 0
    deleted = 0
    updated = 0
    gh_api = github.Github(token)
    for role in Content.objects.filter(is_valid=True, active=True,
                                       id__gt=start, id__lte=end):
        full_name = "{}/{}".format(role.github_user, role.github_repo)
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
            LOG.error(u"FAILED: {0} - {1}".format(full_name, exc))
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
        LOG.error(u"Clear Stuck Imports ERROR: {}".format(exc))
        raise
