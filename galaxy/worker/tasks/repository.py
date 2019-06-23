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

import logging

import celery
import github
import pytz

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from allauth.socialaccount import models as auth_models

from galaxy import constants
from galaxy.importer import repository as i_repo
from galaxy.importer import exceptions as i_exc
from galaxy.main import models
from galaxy.worker import exceptions as exc
from galaxy.worker import importers
from galaxy.worker.importers.validation import validate_contents
from galaxy.worker import logutils
from galaxy.worker import utils
from galaxy.main.celerytasks import user_notifications
from galaxy.api import serializers


LOG = logging.getLogger(__name__)


@celery.task
def import_repository(task_id, user_initiated=False):
    LOG.info(u"Starting task: {:d}".format(int(task_id)))

    try:
        import_task = models.ImportTask.objects.get(id=task_id)
    except models.ImportTask.DoesNotExist:
        LOG.error(u"Failed to get task id: {:d}".format(int(task_id)))
        raise

    import_task.start()

    logger = logging.getLogger('galaxy.worker.tasks.import_repository')
    logger = logutils.ImportTaskAdapter(logger, task=import_task)

    try:
        _import_repository(import_task, logger)
        user_notifications.repo_import.delay(import_task.id, user_initiated)
    except exc.LegacyTaskError as e:
        user_notifications.repo_import.delay(
            import_task.id,
            user_initiated,
            has_failed=True
        )
        import_task.finish_failed(
            reason='Task "{}" failed: {}'.format(import_task.id, str(e)))
    except Exception as e:
        user_notifications.repo_import.delay(
            import_task.id,
            user_initiated,
            has_failed=True
        )
        LOG.exception(e)
        import_task.finish_failed(
            reason='Task "{}" failed: {}'.format(import_task.id, str(e)))
        raise


@transaction.atomic
def _import_repository(import_task, logger):
    repository = import_task.repository
    repo_full_name = (
        repository.provider_namespace.name
        + "/" + repository.original_name)
    logger.info(u'Starting import: task_id={}, repository={}'
                .format(import_task.id, repo_full_name))
    logger.info(' ')

    token = _get_social_token(import_task)
    gh_api = github.Github(token)
    gh_repo = gh_api.get_repo(repo_full_name)

    try:
        repo_info = i_repo.import_repository(
            repository.clone_url,
            branch=import_task.import_branch,
            temp_dir=settings.CONTENT_DOWNLOAD_DIR,
            logger=logger)
    except i_exc.ImporterError as e:
        raise exc.LegacyTaskError(str(e))

    repository.import_branch = repo_info.branch
    repository.format = repo_info.format.value
    repository.travis_status_url = import_task.travis_status_url
    repository.travis_build_url = import_task.travis_build_url

    if repo_info.name:
        old_name = repository.name
        new_name = repo_info.name
        if old_name != new_name:
            logger.info(
                u'Updating repository name "{old_name}" -> "{new_name}"'
                .format(old_name=old_name, new_name=new_name))
            repository.name = new_name

    # NOTE: upon successful import, the role's namespace will get assigned
    # the repo's provider_namespace -> namespace, so that is checked here
    _check_collection_name_conflict(
        ns=repository.provider_namespace.namespace,
        name=repository.name)

    context = utils.Context(
        repository=repository, github_token=token,
        github_client=gh_api, github_repo=gh_repo)

    new_content_objs = []
    for content_info in repo_info.contents:
        content_logger = logutils.ContentTypeAdapter(
            logger, content_info.content_type, content_info.name)
        importer_cls = importers.get_importer(content_info.content_type)
        importer = importer_cls(context, content_info, logger=content_logger)
        issue_tracker_url = ''
        if (hasattr(content_info, 'role_meta')
                and getattr(content_info, 'role_meta')
                and content_info.role_meta.get('issue_tracker_url')):
            issue_tracker_url = content_info.role_meta['issue_tracker_url']
        elif gh_repo.has_issues:
            issue_tracker_url = gh_repo.html_url + '/issues'
        repository.issue_tracker_url = issue_tracker_url

        # NOTE: send importer.models.Content obj to check against db
        content_info = validate_contents([content_info], log=content_logger)[0]

        content_obj = importer.do_import()

        if content_info.scores:
            content_obj.content_score = content_info.scores['content']
            content_obj.metadata_score = content_info.scores['metadata']
            content_obj.quality_score = content_info.scores['quality']
            content_obj.compatibility_score = \
                content_info.scores['compatibility']
            content_obj.save()

        new_content_objs.append(content_obj.id)

    repository.quality_score = repo_info.contents[0].scores['quality']
    repository.quality_score_date = timezone.now()

    for obj in repository.content_objects.exclude(id__in=new_content_objs):
        logger.info(
            'Deleting Content instance: content_type={0}, '
            'namespace={1}, name={2}'.format(
                obj.content_type, obj.namespace, obj.name))
        obj.delete()

    _update_readme(repository, repo_info.readme, gh_api, gh_repo)
    _update_namespace(gh_repo)
    _update_repo_info(repository, gh_repo, repo_info.commit,
                      repo_info.description)
    repository.save()

    _update_task_msg_content_id(import_task)
    _cleanup_old_task_msg(import_task)

    # Updating versions has to go last because:
    # - we don't want to update the version number if the import fails.
    # - version updates send out email notifications and we don't want to
    #   notify people that an update happened if it failed on one of the other
    #   steps
    _update_repository_versions(repository, gh_repo, logger)

    warnings = import_task.messages.filter(
        message_type=models.ImportTaskMessage.TYPE_WARNING).count()
    errors = import_task.messages.filter(
        message_type=models.ImportTaskMessage.TYPE_ERROR).count()
    import_task.finish_success(
        'Import completed with {0} warnings and {1} '
        'errors'.format(warnings, errors))

    if repository.is_new:
        user_notifications.repo_author_release.delay(repository.id)
        repository.is_new = False
        repository.save()

    namespace = repository.provider_namespace.namespace.name

    fields = {
        'content_name': '{}.{}'.format(namespace, repository.name),
        'content_id': repository.id,
        'community_score': repository.community_score,
        'quality_score': repository.quality_score,
    }

    serializers.influx_insert_internal({
        'measurement': 'content_score',
        'fields': fields
    })


def _check_collection_name_conflict(ns, name):
    collections = models.Collection.objects.filter(
        namespace=ns,
        name=name,
    )
    if not collections:
        return
    raise exc.ImportFailed(
        f'A collection ({ns.name}.{name}) under the namespace {ns.name} '
        'already exists, please use a different name for the role '
        'via the meta/main.yml role_name attribute'
    )


def _update_task_msg_content_id(import_task):
    repo_id = import_task.repository.id
    contents = models.Content.objects.filter(repository_id=repo_id)
    name_to_id = {c.original_name: c.id for c in contents}

    # single role repo content_name is None in ImportTaskMessage
    if len(contents) == 1:
        name_to_id[None] = name_to_id[next(iter(name_to_id))]

    import_task_messages = models.ImportTaskMessage.objects.filter(
        task_id=import_task.id,
        is_linter_rule_violation=True
    )

    for msg in import_task_messages:
        if msg.content_name not in name_to_id:
            LOG.warning(u'Importer could not associate content id to rule msg')
            msg.is_linter_rule_violation = False
            msg.save()
            continue
        msg.content_id = name_to_id[msg.content_name]
        msg.save()


def _cleanup_old_task_msg(import_task):
    old_task_ids = models.ImportTask.objects.filter(
        repository=import_task.repository,
    ).exclude(
        id=import_task.id,
    ).values_list(
        'id',
        flat=True,
    )

    if old_task_ids:
        old_task_msgs = models.ImportTaskMessage.objects.filter(
            task__in=old_task_ids
        )
        old_task_msgs.delete()


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
        raise exc.LegacyTaskError(
            u"Failed to get GitHub account for Galaxy user {0}. "
            u"You must first authenticate with GitHub.".format(user.username))


def _update_readme(repository, readme, github_api, github_repo):
    readme_obj = repository.readme
    repository.readme = None
    repository.save()
    repository.readme = utils.update_readme(
        repository, readme_obj, readme, github_api, github_repo)
    repository.save()


def _update_repo_info(repository, gh_repo, commit_info, repo_description):
    if repo_description:
        repository.description = repo_description
    else:
        repository.description = gh_repo.description
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


def _update_repository_versions(repository, github_repo, logger):
    logger.info('Updating repository versions...')

    git_tags = {tag.name: tag for tag in github_repo.get_tags()}
    db_tags = {v.tag: v for v in repository.versions.all()}

    to_delete = set(db_tags) - set(git_tags)
    for version in to_delete:
        db_tags[version].delete()

    to_add = set(git_tags) - set(db_tags)
    tags_added = False
    skipped_tags = []
    for version in to_add:
        tag = git_tags[version]
        try:
            version = utils.parse_version_tag(tag.name)
        except ValueError:
            skipped_tags.append(tag.name)
            continue

        commit_date = tag.commit.commit.author.date.replace(tzinfo=pytz.UTC)
        commit_sha = tag.commit.commit.sha
        version_obj, created = models.RepositoryVersion.objects.get_or_create(
            repository=repository,
            version=version,
            defaults={
                'tag': tag.name,
                'commit_date': commit_date,
                'commit_sha': commit_sha,
            },
        )
        if not created:
            logger.warning('Version conflict: {}'.format(tag.name))
        else:
            tags_added = True

    if skipped_tags:
        msg = ('Galaxy will only import git tags that match the '
               'semantic version format, skipping these tag(s): {}')
        logger.warning(msg.format(', '.join(skipped_tags)))
    if tags_added:
        user_notifications.repo_update.delay(repository.id)

    to_update = set(git_tags) & set(db_tags)
    for version in to_update:
        tag = git_tags[version]
        version_obj = db_tags[version]
        commit_date = tag.commit.commit.author.date.replace(tzinfo=pytz.UTC)
        if version_obj.commit_date != commit_date:
            logger.warning('Release date of version {} has changed.'
                           .format(version_obj.tag))
            version_obj.commit_date = commit_date
            version_obj.commit_sha = tag.commit.commit.sha
            version_obj.save()
