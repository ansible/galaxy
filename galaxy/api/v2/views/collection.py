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
import tarfile

from django.conf import settings
from django.core import exceptions as dj_exc
from django.shortcuts import get_object_or_404

from rest_framework import exceptions as drf_exc
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status as http_codes

from pulpcore.app.serializers import ArtifactSerializer
from pulpcore.app import models as pulp_models

from galaxy import constants
from galaxy.api import base
from galaxy.api import exceptions
from galaxy.api.v2 import serializers
from galaxy.main import models
from galaxy.worker import tasks
from galaxy.common import tasking


__all__ = (
    'CollectionListView',
    'CollectionDetailView',
)


class CollectionExistsError(exceptions.ConflictError):
    default_detail = 'Collection already exists.'
    default_code = 'conflict.collection_exists'


class RepositoryNameError(exceptions.ConflictError):
    default_detail = 'Repository already uses namespace and name.'
    default_code = 'conflict.repository_name_conflict'


class ArtifactExistsError(exceptions.ConflictError):
    default_detail = 'Artifact already exists.'
    default_code = 'conflict.artifact_exists'


class ArtifactInvalidError(exceptions.ValidationError):
    default_detail = 'Artifact not a valid tar archive file.'
    default_code = 'invalid.artifact_invalid_tarfile'


class ArtifactMaxSizeError(exceptions.ValidationError):
    default_detail = 'Artifact exceeds maximum size.'
    default_code = 'invalid.artifact_exceeds_max_size'


class CollectionDetailView(base.APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        """Return a collection."""
        collection = self._get_collection()
        serializer = serializers.CollectionSerializer(
            collection, context={'request': request})
        return Response(serializer.data)

    def _get_collection(self):
        """Get collection from either id, or namespace and name."""
        pk = self.kwargs.get('pk', None)
        ns_name = self.kwargs.get('namespace', None)
        name = self.kwargs.get('name', None)

        if pk:
            return get_object_or_404(models.Collection, pk=pk)
        ns = get_object_or_404(models.Namespace, name=ns_name)
        return get_object_or_404(models.Collection, namespace=ns, name=name)


class CollectionListView(base.ListAPIView):
    queryset = models.Collection.objects.only(
        'id',
        'name',
        'deprecated',
        'created',
        'modified',
        'namespace__name',
        'latest_version__version'
    ).select_related(
        'namespace',
        'latest_version',
    ).all()
    serializer_class = serializers.CollectionSerializer

    def get(self, request, *args, **kwargs):
        """List Ansible Collections."""
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
        self._check_max_file_size(request.data['file'].size)
        self._check_role_name_conflict(namespace, filename.name)
        self._check_multi_repo_name_conflict(namespace, filename.name)
        self._check_version_conflict(namespace, filename)
        self._check_is_tarfile(request.data['file'].file.name)

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
                                args=[task.pk], request=request)}
        return Response(data, status=http_codes.HTTP_202_ACCEPTED)

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [IsAuthenticated]
        else:
            # OPTIONS and GET requests
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def _get_namespace(self, data):
        """Get collecton namespace from filename."""
        ns_name = data['filename'].namespace
        try:
            return models.Namespace.objects.get(name=ns_name)
        except models.Namespace.DoesNotExist:
            raise exceptions.ValidationError(
                f'Namespace "{ns_name}" does not exist.'
            )

    def _check_namespace_access(self, namespace, user):
        """Validate that collection namespace exists and user owns it."""
        if not namespace.owners.filter(id=user.id).count():
            raise exceptions.PermissionDenied(
                'The namespace listed on your filename must match one of '
                'the namespaces you have access to.'
            )

    def _check_max_file_size(self, file_size):
        """Validate artifact file size does not exceed maximum."""
        # NOTE: this method does not check the file size before upload,
        # but checks after the file is uploaded to the server
        if file_size > constants.MAX_UPLOAD_FILE_SIZE_BYTES:
            raise ArtifactMaxSizeError(
                f'Artifact size ({file_size}) exceeds maximum file size: '
                f'{constants.MAX_UPLOAD_FILE_SIZE_BYTES} bytes'
            )

    def _check_role_name_conflict(self, ns, name):
        roles = models.Content.objects.filter(
            content_type__name=constants.ContentType.ROLE,
            repository__provider_namespace__namespace=ns,
            name=name,
        )
        if not roles:
            return
        raise RepositoryNameError(
            f'A role ({ns.name}.{name}) under the namespace {ns.name} '
            'already exists, please use a different name for the collection, '
            'or delete the role, '
            'or rename the role via the meta/main.yml role_name attribute'
        )

    def _check_multi_repo_name_conflict(self, ns, name):
        multi_content_repos = models.Repository.objects.filter(
            format='multi',
            provider_namespace__namespace=ns,
            name__iexact=name,
        )
        if not multi_content_repos:
            return
        raise RepositoryNameError(
            f'A multi-content repo ({ns.name}.{name}) under the '
            f'namespace {ns.name} already exists. '
            'Multi-content repos are deprecated in favor of collections. '
            'You can delete the multi-content repo and '
            're-import the collection.'
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
            raise CollectionExistsError(
                f'Collection "{filename.namespace}-{filename.name}'
                f'-{filename.version}" already exists.')

    def _check_is_tarfile(self, file):
        """Validate artifact is tarfile in view, before importer starts."""
        if not tarfile.is_tarfile(file):
            raise ArtifactInvalidError('Artifact not valid tar archive file.')

    def _save_artifact(self, data):
        artifact_serializer = ArtifactSerializer(data=data)
        try:
            artifact_serializer.is_valid(raise_exception=True)
        except drf_exc.ValidationError as e:
            error_codes = e.get_codes()
            if 'unique' in error_codes.get('non_field_errors', []):
                raise ArtifactExistsError()
            raise
        return artifact_serializer.save()


class SubscribedListView(CollectionListView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise exceptions.NotAuthenticated()
        user_prefs, created = models.UserPreferences.objects.get_or_create(
            pk=self.request.user.pk
        )

        return user_prefs.collections_followed.only(
            'id',
            'name',
            'deprecated',
            'created',
            'modified',
            'namespace__name',
            'latest_version__version'
        ).select_related(
            'namespace',
            'latest_version',
        ).all()
