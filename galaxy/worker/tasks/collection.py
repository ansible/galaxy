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

from galaxy.common import logutils
from galaxy.common import schema
from galaxy.importer import collection as i_collection
from galaxy.importer import exceptions as i_exc
from galaxy.main import models
from galaxy.worker import exceptions as exc


log = logging.getLogger(__name__)


def import_collection(
        artifact_id, repository_id, task_id):
    task = models.CollectionImport.current()
    log.info('Starting collection import task: {}'.format(task.id))

    filename = schema.CollectionFilename(
        task.namespace.name, task.name, task.version)

    artifact = pulp_models.Artifact.objects.get(pk=artifact_id)
    repository = pulp_models.Repository.objects.get(pk=repository_id)
    import_task = models.ImportTask.objects.get(id=task_id)
    log_db = _get_import_task_msg_logger(import_task)

    import_task.start()
    log_db.info('Starting import: task_id={}, artifact_pk={}'.format(
                import_task.id, artifact_id))

    try:
        collection_info = _process_collection(artifact, filename, log_db)
        with transaction.atomic():
            coll, coll_ver = _publish_collection(
                artifact, repository, task.namespace, collection_info)
        _process_import_success(coll, coll_ver, import_task)
    except i_exc.ImporterError as e:
        _process_import_fail(artifact, import_task, msg=e)
    except exc.VersionConflict:
        msg = 'Collection version already exists in galaxy'
        _process_import_fail(artifact, import_task, msg)
    except Exception as e:
        _process_import_fail(artifact, import_task, msg=e.__class__.__name__)
        raise exc.PulpTaskError(str(e))


def _get_import_task_msg_logger(import_task):
    log_db = logging.getLogger('galaxy.worker.tasks.import_repository')
    log_db = logutils.ImportTaskAdapter(log_db, task=import_task)
    return log_db


def _process_collection(artifact, filename, log_db):
    with tempfile.TemporaryDirectory() as pkg_dir:
        with artifact.file.open() as pkg_file, \
                tarfile.open(fileobj=pkg_file) as pkg_tar:
            pkg_tar.extractall(pkg_dir)
        collection_info = i_collection.import_collection(
            pkg_dir, filename, log_db)
        _log_collection_loaded(collection_info)

    return collection_info


def _publish_collection(artifact, repository, namespace, collection_info):
    metadata = collection_info.collection_info
    collection, _ = models.Collection.objects.update_or_create(
        namespace=namespace,
        name=metadata.name,
    )

    try:
        collection_version, is_created = collection.versions.get_or_create(
            collection=collection,
            version=metadata.version,
            defaults={
                'metadata': metadata.get_json(),
                'quality_score': collection_info.quality_score,
                'contents': collection_info.contents,
            },
        )
    except IntegrityError as e:
        # catches dup key value "(collection_id, version)=... already exists"
        raise exc.VersionConflict(str(e))
    if not is_created:
        raise exc.VersionConflict()

    relative_path = '{0}-{1}-{2}.tar.gz'.format(
        metadata.namespace,
        metadata.name,
        metadata.version
    )
    pulp_models.ContentArtifact.objects.create(
        artifact=artifact,
        content=collection_version,
        relative_path=relative_path,
    )
    with pulp_models.RepositoryVersion.create(repository) as new_version:
        new_version.add_content(
            pulp_models.Content.objects.filter(pk=collection_version.pk)
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
    return collection, collection_version


def _process_import_success(collection, coll_ver, import_task):
    import_task.collection = collection

    warnings = import_task.messages.filter(
        message_type=models.ImportTaskMessage.TYPE_WARNING).count()
    errors = import_task.messages.filter(
        message_type=models.ImportTaskMessage.TYPE_ERROR).count()
    log_entry = 'Import completed with {0} warnings and {1} ' \
                'errors'.format(warnings, errors)
    log.info(log_entry)
    import_task.finish_success(log_entry)


def _process_import_fail(artifact, import_task, msg):
    # Delete artifact file and model if import failed
    artifact.file.delete(save=False)
    artifact.delete()

    log_entry = 'Import Task "{}" failed: {}'.format(import_task.id, msg)
    log.error(log_entry)
    import_task.finish_failed(reason=log_entry)


def _log_collection_loaded(coll_info):
    log.debug('Collection loaded - metadata={}, quality_score={}'.format(
        coll_info.collection_info.__dict__,
        coll_info.quality_score
    ))
    for content in coll_info.contents:
        log.debug('Content: type={} name={} scores={}'.format(
            content['content_type'],
            content['name'],
            content['scores'],
        ))
