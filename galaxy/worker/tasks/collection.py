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

import logging

from django.db import transaction
from django.db.utils import IntegrityError
from galaxy_importer.collection import import_collection as process_collection
from galaxy_importer.collection import CollectionFilename
from galaxy_importer.exceptions import ImporterError
from pulpcore.app import models as pulp_models
import semantic_version as semver

from galaxy.main import models
from galaxy.main.celerytasks import user_notifications
from galaxy.worker import exceptions as exc
from galaxy.worker import logutils
from galaxy.worker.importers.collection import check_dependencies


log = logging.getLogger(__name__)

ARTIFACT_REL_PATH = '{namespace}-{name}-{version}.tar.gz'

CONTENT_TYPE_MAP = {
    'role': 'role',
    'module': 'module',
    'module_utils': 'module_utils',
    'action': 'action_plugin',
    'become': 'become_plugin',
    'cache': 'cache_plugin',
    'callback': 'callback_plugin',
    'cliconf': 'cliconf_plugin',
    'connection': 'connection_plugin',
    'doc_fragments': 'doc_fragments_plugin',
    'filter': 'filter_plugin',
    'httpapi': 'httpapi_plugin',
    'inventory': 'inventory_plugin',
    'lookup': 'lookup_plugin',
    'netconf': 'netconf_plugin',
    'shell': 'shell_plugin',
    'strategy': 'strategy_plugin',
    'terminal': 'terminal_plugin',
    'test': 'test_plugin',
    'vars': 'vars_plugin',
}


def import_collection(artifact_id, repository_id):
    task = models.CollectionImport.current()
    log.info(f'Starting collection import task: {task.id}')

    artifact = pulp_models.Artifact.objects.get(pk=artifact_id)
    repository = pulp_models.Repository.objects.get(pk=repository_id)

    filename = CollectionFilename(
        task.namespace.name, task.name, task.version)

    task_logger = _get_task_logger(task)
    task_logger.info(
        f'Starting import: task_id={task.id}, artifact_id={artifact_id}')

    try:
        importer_data = _process_collection(artifact, filename, task_logger)
        task_logger.info('Publishing collection')
        version = _publish_collection(
            task, artifact, repository, importer_data)
        task_logger.info('Collection published')
    except Exception as e:
        task_logger.error(f'Import Task "{task.id}" failed: {e}')
        user_notifications.collection_import.delay(task.id, has_failed=True)
        artifact.delete()
        raise

    _notify_followers(version)

    user_notifications.collection_import.delay(task.id, has_failed=False)
    errors, warnings = task.get_message_stats()
    task_logger.info(
        f'Import completed with {warnings} warnings and {errors} errors')


def _get_task_logger(task):
    logger = logging.getLogger('galaxy.worker.tasks.import_collection')
    return logutils.ImportTaskAdapter(logger, task=task)


def _process_collection(artifact, filename, task_logger):
    try:
        with artifact.file.open() as artifact_file:
            importer_data = process_collection(
                artifact_file, filename=filename, logger=task_logger
            )
    except ImporterError as e:
        log.error(f'Collection processing was not successfull: {e}')
        raise
    task_logger.info('Processing via galaxy-importer complete')

    importer_data = _transform_importer_data(importer_data)

    task_logger.info('Checking dependencies in importer data')
    check_dependencies(importer_data['metadata']['dependencies'])

    return importer_data


def _transform_importer_data(data):
    """Update data from galaxy_importer to match values in Community Galaxy."""

    for c in data['contents']:
        c['content_type'] = CONTENT_TYPE_MAP.get(
            c['content_type'], c['content_type'])
        c['scores'] = None
        c['metadata'] = {}
        c['role_meta'] = None
        c['description'] = c['description'] or ''

    return data


@transaction.atomic
def _publish_collection(task, artifact, repository, importer_data):
    collection, _ = models.Collection.objects.get_or_create(
        namespace=task.namespace, name=importer_data['metadata']['name'])

    try:
        version = collection.versions.create(
            version=importer_data['metadata']['version'],
            metadata=importer_data['metadata'],
            quality_score=None,
            contents=importer_data['contents'],
            readme_mimetype='text/markdown',
            readme_text='',
            readme_html=importer_data['docs_blob']['collection_readme']['html']
        )
    except IntegrityError:
        raise exc.VersionConflict(
            'Collection version "{version}" already exists.'
            .format(version=importer_data['metadata']['version']))

    _update_latest_version(collection, version)
    log.info('Updating collection tags')
    _update_collection_tags(collection, version, importer_data['metadata'])

    log.info('Creating pulp_models.ContentArtifact')
    rel_path = ARTIFACT_REL_PATH.format(
        namespace=importer_data['metadata']['namespace'],
        name=importer_data['metadata']['name'],
        version=importer_data['metadata']['version'])
    pulp_models.ContentArtifact.objects.create(
        artifact=artifact,
        content=version,
        relative_path=rel_path,
    )

    log.info('Creating pulp_models.RepositoryVersion')
    with pulp_models.RepositoryVersion.create(repository) as new_version:
        new_version.add_content(
            pulp_models.Content.objects.filter(pk=version.pk)
        )

    log.info('Creating pulp_models.publication')
    publication = pulp_models.Publication.objects.create(
        repository_version=new_version,
        complete=True,
        pass_through=True,
    )
    log.info('Creating pulp_models.publication')
    pulp_models.Distribution.objects.update_or_create(
        name='galaxy',
        base_path='galaxy',
        defaults={'publication': publication},
    )

    task.imported_version = version
    log.info('Saving task')
    task.save()
    log.info('task saved')
    return version


def _update_latest_version(collection, new_version):
    latest_version = collection.latest_version
    if latest_version is None or (semver.Version(latest_version.version)
                                  < semver.Version(new_version.version)):
        collection.latest_version = new_version
        collection.save()


def _update_collection_tags(collection, version, metadata):
    """Update tags at collection-level, only if highest version."""

    if collection.latest_version != version:
        return

    tags_not_in_db = [
        {'name': tag, 'description': tag, 'active': True}
        for tag in metadata['tags']
        if models.Tag.objects.filter(name=tag).count() == 0]
    models.Tag.objects.bulk_create([models.Tag(**t) for t in tags_not_in_db])

    tags_qs = models.Tag.objects.filter(name__in=metadata['tags'])
    collection.tags.add(*tags_qs)

    tags_not_in_metadata = [
        tag for tag in collection.tags.all()
        if tag.name not in metadata['tags']
    ]
    collection.tags.remove(*tags_not_in_metadata)


def _notify_followers(version):
    user_notifications.collection_new_version.delay(version.pk)
    is_first_version = (version.collection.versions.count() == 1)
    if is_first_version:
        user_notifications.coll_author_release.delay(version.pk)
