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
from django.core.exceptions import ObjectDoesNotExist
from pulpcore.app import models as pulp_models

from galaxy.main import models
from galaxy.importer import collection as i_collection
from galaxy.importer import exceptions as i_exc

log = logging.getLogger(__name__)


class VersionConflict(Exception):
    pass


class PulpTaskError(Exception):
    pass


@transaction.atomic
def import_collection(artifact_pk, repository_pk):
    artifact = pulp_models.Artifact.objects.get(pk=artifact_pk)
    repository = pulp_models.Repository.objects.get(pk=repository_pk)

    try:
        importer_coll = i_collection.import_collection(artifact, log)
    except i_exc.ImporterError as e:
        raise PulpTaskError(str(e))

    collection_info = importer_coll.collection_info
    contents = importer_coll.contents

    log.debug('collection loaded: collection metadata=%s', collection_info)
    log.debug('collection quality_score=%s', importer_coll.quality_score)
    for c in contents:
        c_info = 'content: type={} name={}'.format(c.content_type, c.name)
        if c.scores:
            log.debug('{} score={}'.format(c_info, c.scores['quality']))
        else:
            log.debug(c_info)

    try:
        namespace = models.Namespace.objects.get(
            name=collection_info.namespace)
    except ObjectDoesNotExist as e:
        raise PulpTaskError(str(e))

    collection, _ = models.Collection.objects.get_or_create(
        namespace=namespace,
        name=collection_info.name,
    )
    collection_version, is_created = collection.versions.get_or_create(
        collection=collection,
        version=collection_info.version,
        metadata=collection_info.get_json(),
    )
    if not is_created:
        raise VersionConflict()

    relative_path = '{0}-{1}-{2}.tar.gz'.format(
        collection_info.namespace,
        collection_info.name,
        collection_info.version
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
