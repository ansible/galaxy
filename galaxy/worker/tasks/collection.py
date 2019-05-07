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
import tempfile
import tarfile

from django.db import transaction
from django.db.utils import IntegrityError
from pulpcore.app import models as pulp_models

from galaxy.common import schema
from galaxy.importer import collection as importer
from galaxy.importer import exceptions as i_exc
from galaxy.main import models
from galaxy.worker import exceptions as exc
from galaxy.worker import logutils


log = logging.getLogger(__name__)

ARTIFACT_REL_PATH = '{namespace}-{name}-{version}.tar.gz'


def import_collection(artifact_id, repository_id):
    task = models.CollectionImport.current()
    log.info('Starting collection import task: {}'.format(task.id))

    artifact = pulp_models.Artifact.objects.get(pk=artifact_id)
    repository = pulp_models.Repository.objects.get(pk=repository_id)

    filename = schema.CollectionFilename(
        task.namespace.name, task.name, task.version)

    task_logger = _get_task_logger(task)
    task_logger.info('Starting import: task_id={}, artifact_id={}'
                     .format(task.id, artifact_id))
    try:
        collection_info = _process_collection(
            artifact, filename, task_logger)
        _publish_collection(task, artifact, repository, collection_info)
    except Exception as e:
        artifact.delete()
        task_logger.error('Import Task "{task_id}" failed: {message}'
                          .format(task_id=task.id, message=str(e)))
        raise

    warnings, errors = task.get_message_stats()
    msg = ('Import completed with {warnings} warnings and {errors} errors'
           .format(warnings=warnings, errors=errors))
    task_logger.info(msg)


def _get_task_logger(task):
    logger = logging.getLogger('galaxy.worker.tasks.import_collection')
    return logutils.ImportTaskAdapter(logger, task=task)


def _process_collection(artifact, filename, task_logger):
    with tempfile.TemporaryDirectory() as extract_dir:
        with artifact.file.open() as pkg_file, \
                tarfile.open(fileobj=pkg_file) as pkg_tar:
            pkg_tar.extractall(extract_dir)

        try:
            collection_info = importer.import_collection(
                extract_dir, filename, task_logger)
        except i_exc.ImporterError as e:
            raise exc.ImportFailed(str(e))

    _log_collection_info(collection_info)
    return collection_info


@transaction.atomic
def _publish_collection(task, artifact, repository, collection_info):
    metadata = collection_info.collection_info
    collection, _ = models.Collection.objects.get_or_create(
        namespace=task.namespace, name=metadata.name)

    try:
        version = collection.versions.create(
            version=metadata.version,
            metadata=metadata.get_json(),
            quality_score=collection_info.quality_score,
            contents=collection_info.contents,
            readme_mimetype=collection_info.readme['mimetype'],
            readme_text=collection_info.readme['text'],
            readme_html=collection_info.readme['html'],
        )
    except IntegrityError:
        raise exc.VersionConflict(
            'Collection version "{version}" already exists.'
            .format(version=metadata.version))

    _update_collection_tags(collection, version, metadata)

    rel_path = ARTIFACT_REL_PATH.format(
        namespace=metadata.namespace, name=metadata.name,
        version=metadata.version)
    pulp_models.ContentArtifact.objects.create(
        artifact=artifact,
        content=version,
        relative_path=rel_path,
    )

    with pulp_models.RepositoryVersion.create(repository) as new_version:
        new_version.add_content(
            pulp_models.Content.objects.filter(pk=version.pk)
        )

    publication = pulp_models.Publication.objects.create(
        repository_version=new_version,
        complete=True,
        pass_through=True,
    )
    pulp_models.Distribution.objects.update_or_create(
        name='galaxy',
        base_path='galaxy',
        defaults={'publication': publication},
    )

    task.imported_version = version
    task.save()


def _update_collection_tags(collection, version, metadata):
    '''Update tags at collection-level, only if highest version'''

    if collection.highest_version != version:
        return

    tags_not_in_db = [
        {'name': tag, 'description': tag, 'active': True}
        for tag in metadata.tags
        if models.Tag.objects.filter(name=tag).count() == 0]
    models.Tag.objects.bulk_create([models.Tag(**t) for t in tags_not_in_db])

    tags_qs = models.Tag.objects.filter(name__in=metadata.tags)
    collection.tags.add(*tags_qs)

    tags_not_in_metadata = [
        tag for tag in collection.tags.all()
        if tag.name not in metadata.tags
    ]
    collection.tags.remove(*tags_not_in_metadata)


def _log_collection_info(collection_info):
    log.debug('Collection loaded - metadata={}, quality_score={}'.format(
        collection_info.collection_info.__dict__,
        collection_info.quality_score
    ))
    for content in collection_info.contents:
        log.debug('Content: type={} name={} scores={}'.format(
            content['content_type'],
            content['name'],
            content['scores'],
        ))
