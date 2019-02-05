from django.conf import settings
from rest_framework import views
from rest_framework import status as status_codes
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import IsAuthenticated

from pulpcore.app.serializers import ArtifactSerializer
from pulpcore.app.response import OperationPostponedResponse
from pulpcore.tasking.tasks import enqueue_with_reservation
from pulpcore.app import models as pulp_models

from galaxy.api.serializers import collection as serializers
from galaxy.pulp import tasks


__all__ = [
    'UploadCollectionView'
]


class CollectionExistsError(APIException):
    status_code = status_codes.HTTP_409_CONFLICT
    default_detail = 'Collection already exists.'
    default_code = 'collection_exists'


class UploadCollectionView(views.APIView):

    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        """Upload an Ansible Collection."""

        serializer = serializers.UploadCollectionSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        artifact_data = {'file': request.data['file']}
        if serializer.data['sha256'] is not None:
            artifact_data['sha256'] = data['sha256']

        repository = pulp_models.Repository.objects.get(
            name=settings.GALAXY_PULP_REPOSITORY)

        artifact = self._save_artifact(artifact_data)

        async_result = enqueue_with_reservation(
            tasks.import_collection, [],
            kwargs={
                'artifact_pk': artifact.pk,
                'repository_pk': repository.pk
            })
        return OperationPostponedResponse(async_result, request)

    def _save_artifact(self, data):
        artifact_serializer = ArtifactSerializer(data=data)
        try:
            artifact_serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error_codes = e.get_codes()
            if 'unique' in error_codes.get('non_field_errors', []):
                raise CollectionExistsError()
            raise
        return artifact_serializer.save()
