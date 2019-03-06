from django.conf import settings
from rest_framework import views
from rest_framework import status as status_codes
import rest_framework.exceptions as drf_exc
from rest_framework.permissions import IsAuthenticated

from pulpcore.app.serializers import ArtifactSerializer
from pulpcore.app.response import OperationPostponedResponse
from pulpcore.tasking.tasks import enqueue_with_reservation
from pulpcore.app import models as pulp_models

from galaxy.api.serializers import collection as serializers
from galaxy.main import models
from galaxy.pulp import tasks

__all__ = [
    'UploadCollectionView'
]


class CollectionExistsError(drf_exc.APIException):
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

        # TODO(cutwater): Merge Artifact and UploadCollectionSerializers
        # TODO(cutwater): Extract namespace and name from `METADATA.json`
        #                 and validate that collection name matches filename.
        self._validate_namespace(request.user, data)

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

    def _validate_namespace(self, user, data):
        """Validate that collection namespace exists and user owns it."""
        ns_name = data['filename'].namespace
        try:
            ns = models.Namespace.objects.get(name=ns_name)
        except models.Namespace.DoesNotExist:
            raise drf_exc.ValidationError(
                'Namespace {0} does not exist'.format(ns_name))

        if not ns.owners.filter(id=user.id).count():
            raise drf_exc.PermissionDenied(
                'The namespace listed on your filename must match one of ' +
                'the namespaces you have access to.'
            )

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
