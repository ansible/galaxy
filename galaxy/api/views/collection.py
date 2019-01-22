from django.conf import settings
from rest_framework import views
from rest_framework.permissions import IsAuthenticated

from pulpcore.app.viewsets import TaskViewSet as _TaskViewSet
from pulpcore.app.serializers import ArtifactSerializer
from pulpcore.app.response import OperationPostponedResponse
from pulpcore.tasking.tasks import enqueue_with_reservation
from pulpcore.app import models as pulp_models

from galaxy.api.serializers import collection as serializers
from galaxy.pulp import tasks


__all__ = [
    'TaskViewSet',
    'UploadCollectionView'
]


class TaskViewSet(_TaskViewSet):

    permission_classes = (IsAuthenticated, )


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
        artifact_serializer.is_valid(raise_exception=True)
        return artifact_serializer.save()
