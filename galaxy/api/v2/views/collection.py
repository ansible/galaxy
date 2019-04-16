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
from django.conf import settings
from django.core import exceptions as dj_exc
from django.shortcuts import get_object_or_404

from rest_framework import exceptions as drf_exc
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status as status_codes
from rest_framework import views

from pulpcore.app.serializers import ArtifactSerializer
from pulpcore.app import models as pulp_models

from galaxy.api.exceptions import CollectionExistsError
from galaxy.api.v2 import serializers
from galaxy.main import models
from galaxy.worker import tasks
from galaxy.common import tasking


__all__ = (
    'CollectionListView',
    'CollectionDetailView',
)


# FIXME(cutwater): Implement consistent error reporting format.


class CollectionDetailView(views.APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        """Return a collection."""
        collection = self._get_collection(kwargs)
        serializer = serializers.CollectionSerializer(collection)
        return Response(serializer.data)

    def _get_collection(self, kwargs):
        """Get collection from either id, or namespace and name."""
        pk = kwargs.get('pk', None)
        ns_name = kwargs.get('namespace', None)
        name = kwargs.get('name', None)

        if pk:
            return get_object_or_404(models.Collection, pk=pk)
        ns = get_object_or_404(models.Namespace, name=ns_name)
        return get_object_or_404(models.Collection, namespace=ns, name=name)


class CollectionListView(views.APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        """Upload an Ansible Collection."""

        serializer = serializers.CollectionUploadSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        filename = data['filename']

        # TODO(cutwater): Merge Artifact and UploadCollectionSerializers
        namespace = self._get_namespace(data)
        self._check_namespace_access(namespace, request.user)
        self._check_version_conflict(namespace, filename)

        artifact_data = {'file': request.data['file']}
        if serializer.data['sha256'] is not None:
            artifact_data['sha256'] = data['sha256']

        repository = pulp_models.Repository.objects.get(
            name=settings.GALAXY_PULP_REPOSITORY)

        artifact = self._save_artifact(artifact_data)

        task = tasking.create_task(
            tasks.import_collection,
            task_cls=models.CollectionImport,
            params={
                'artifact_id': artifact.pk,
                'repository_id': repository.pk,
            },
            task_args={
                'namespace': namespace,
                'name': filename.name,
                'version': filename.version,
            })

        data = {'task': reverse('api:v2:collection-import-detail',
                                args=[task.pk], request=None)}
        return Response(data, status=status_codes.HTTP_202_ACCEPTED)

    def _get_namespace(self, data):
        """Get collecton namespace from filename."""
        ns_name = data['filename'].namespace
        try:
            return models.Namespace.objects.get(name=ns_name)
        except models.Namespace.DoesNotExist:
            raise drf_exc.ValidationError(
                'Namespace "{0}" does not exist.'.format(ns_name))

    def _check_namespace_access(self, namespace, user):
        """Validate that collection namespace exists and user owns it."""
        if not namespace.owners.filter(id=user.id).count():
            raise drf_exc.PermissionDenied(
                'The namespace listed on your filename must match one of '
                'the namespaces you have access to.'
            )

    def _check_version_conflict(self, namespace, filename):
        """Validate that uploaded collection version does not exist."""
        try:
            collection = models.Collection.objects.get(
                namespace=namespace, name=filename.name)
            collection.versions.get(version=filename.version)
        except dj_exc.ObjectDoesNotExist:
            pass
        else:
            raise CollectionExistsError()

    def _save_artifact(self, data):
        artifact_serializer = ArtifactSerializer(data=data)
        try:
            artifact_serializer.is_valid(raise_exception=True)
        except drf_exc.ValidationError as e:
            error_codes = e.get_codes()
            if 'unique' in error_codes.get('non_field_errors', []):
                raise CollectionExistsError()
            raise
        return artifact_serializer.save()
