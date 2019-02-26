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

from galaxy.main import models
from galaxy.importer import collection as i_collection
from galaxy.importer import exceptions as i_exc


log = logging.getLogger(__name__)


# TODO(cutwater): Move to exceptions module
# TODO(cutwater): Better exception hierarchy
class VersionConflict(Exception):
    pass


class PulpTaskError(Exception):
    pass


def import_collection(artifact_pk, repository_pk, namespace_pk):
    artifact = pulp_models.Artifact.objects.get(pk=artifact_pk)
    repository = pulp_models.Repository.objects.get(pk=repository_pk)

    try:
        with transaction.atomic():
            collection_info = _process_collection(artifact)
            _publish_collection(artifact, repository,
                                namespace_pk, collection_info)
    except Exception:
        # Delete artifact file and model if import failed
        artifact.file.delete(save=False)
        artifact.delete()
        raise


def _process_collection(artifact):
    with tempfile.TemporaryDirectory() as pkg_dir:
        with artifact.file.open() as pkg_file, \
                tarfile.open(fileobj=pkg_file) as pkg_tar:
            pkg_tar.extractall(pkg_dir)
        try:
            collection_info = i_collection.import_collection(pkg_dir, log)
        except i_exc.ImporterError as e:
            raise PulpTaskError(str(e))

        _log_collection_loaded(collection_info)

        return collection_info


def _log_collection_loaded(collection_info):
    log.debug('collection metadata=%s',
              collection_info.collection_info.__dict__)
    log.debug('collection quality_score=%s', collection_info.quality_score)
    for c in collection_info.contents:
        c_info = 'content: type={} name={}'.format(c.content_type, c.name)
        if c.scores:
            log.debug('{} score={}'.format(c_info, c.scores['quality']))
        else:
            log.debug(c_info)


def _publish_collection(artifact, repository, namespace_pk, collection_info):
    metadata = collection_info.collection_info
    collection, _ = models.Collection.objects.update_or_create(
        namespace_id=namespace_pk,
        name=metadata.name,
    )

    try:
        collection_version, is_created = collection.versions.get_or_create(
            collection=collection,
            version=metadata.version,
            defaults={
                'metadata': metadata.get_json(),
                'quality_score': collection_info.quality_score,
            },
        )
    except IntegrityError as e:
        # catches dup key value "(collection_id, version)=... already exists"
        raise VersionConflict(str(e))
    if not is_created:
        raise VersionConflict()

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
    log.info('Imported artifact: %s', relative_path)
