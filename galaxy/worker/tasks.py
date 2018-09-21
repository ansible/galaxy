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
from numbers import Number

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
    LOG.info(u"Starting task: {:d}".format(int(task_id)))

    try:
        import_task = models.ImportTask.objects.get(id=task_id)
    except models.ImportTask.DoesNotExist:
        LOG.error(u"Failed to get task id: {:d}".format(int(task_id)))
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
            temp_dir=settings.CONTENT_DOWNLOAD_DIR,
            logger=logger)
    except i_exc.ImporterError as e:
        raise exc.TaskError(str(e))

    repository.import_branch = repo_info.branch
    repository.format = repo_info.format.value

    if repo_info.name:
        old_name = repository.name
        new_name = repo_info.name
        if old_name != new_name:
            logger.info(
                u'Updating repository name "{old_name}" -> "{new_name}"'
                .format(old_name=old_name, new_name=new_name))
            repository.name = new_name

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
        content_obj = importer.do_import()
        new_content_objs.append(content_obj.id)

    for obj in repository.content_objects.exclude(id__in=new_content_objs):
        logger.info(
            'Deleting Content instance: content_type={0}, '
            'namespace={1}, name={2}'.format(
                obj.content_type, obj.namespace, obj.name))
        obj.delete()

    _update_readme(repository, repo_info.readme, gh_api, gh_repo)
    _update_repository_versions(repository, gh_repo, logger)
    _update_namespace(gh_repo)
    _update_repo_info(repository, gh_repo, repo_info.commit,
                      repo_info.description)
    repository.save()

    _update_task_msg_content_id(import_task)
    _update_task_msg_severity(import_task)
    _update_quality_score(import_task)

    warnings = import_task.messages.filter(
        message_type=models.ImportTaskMessage.TYPE_WARNING).count()
    errors = import_task.messages.filter(
        message_type=models.ImportTaskMessage.TYPE_ERROR).count()
    import_task.finish_success(
        'Import completed with {0} warnings and {1} '
        'errors'.format(warnings, errors))


def _update_task_msg_content_id(import_task):
    repo_id = import_task.repository.id
    contents = models.Content.objects.filter(repository_id=repo_id)
    name_to_id = {c.original_name: c.id for c in contents}

    # single role repo content_name is None in ImportTaskMessage
    if len(contents) == 1:
        name_to_id[None] = name_to_id[name_to_id.keys()[0]]

    import_messages = models.ImportTaskMessage.objects.filter(
        task_id=import_task.id,
        is_linter_rule_violation=True
    )

    for msg in import_messages:
        if msg.content_name not in name_to_id:
            LOG.error(u'Importer could not associate content id to rule msg')
            msg.is_linter_rule_violation = False
            msg.save()
            continue
        msg.content_id = name_to_id[msg.content_name]
        msg.save()


def _update_task_msg_severity(import_task):
    rule_to_severity = {'{}_{}'.format(r.linter_id, r.rule_id).lower():
                        r.severity
                        for r in models.ContentRule.objects.all()}

    import_messages = models.ImportTaskMessage.objects.filter(
        task_id=import_task.id,
        is_linter_rule_violation=True
    )

    for msg in import_messages:
        rule_code = '{}_{}'.format(msg.linter_type,
                                   msg.linter_rule_id).lower()
        if rule_code not in rule_to_severity:
            LOG.warning(u'Rule not found in database: {}'.format(rule_code))
            msg.is_linter_rule_violation = False
            msg.save()
            continue
        msg.rule_severity = rule_to_severity[rule_code]
        msg.save()


def _update_quality_score(import_task):
    BASE_SCORE = 50
    SEVERITY_TO_WEIGHT = {
        0: 0,
        1: 0.75,
        2: 1.25,
        3: 2.5,
        4: 5,
        5: 10,
    }

    rule_to_severity = {'{}_{}'.format(r.linter_id, r.rule_id).lower():
                        r.severity
                        for r in models.ContentRule.objects.all()}
    repository = import_task.repository
    contents = models.Content.objects.filter(repository_id=repository.id)
    repo_points = 0.0

    for content in contents:
        messages = models.ImportTaskMessage.objects.filter(
            task_id=import_task.id,
            content_id=content.id,
            is_linter_rule_violation=True,
        )

        rule_vios = ['{}_{}'.format(m.linter_type, m.linter_rule_id).lower()
                     for m in messages]
        severitys = [rule_to_severity[rule_vio] for rule_vio in rule_vios
                     if rule_vio in rule_to_severity]
        weights = [SEVERITY_TO_WEIGHT[s] for s in severitys
                   if isinstance(SEVERITY_TO_WEIGHT[s], Number)]
        score = max(0.0, (BASE_SCORE - sum(weights)) / 10)

        content.content_score = score
        content.quality_score = score
        content.save()
        repo_points += score

        score_calc_log = ('score calc for content {} - '
                          'rule_vios, severitys, weights, score: '
                          '{}, {}, {}, {}')
        LOG.debug(score_calc_log.format(content.original_name,
                                        rule_vios, severitys, weights,
                                        content.quality_score))

    repository.quality_score = repo_points / contents.count()
    repository.save()
    LOG.debug(u'repo quality score: {}'.format(repository.quality_score))


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
    for version in to_add:
        tag = git_tags[version]
        try:
            version = utils.parse_version_tag(tag.name)
        except ValueError:
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
