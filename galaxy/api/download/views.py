import logging
from pathlib import PurePath

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.shortcuts import redirect
from storages.backends import s3boto3
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny

from galaxy.api.base import APIView
from galaxy.common.schema import CollectionFilename
from galaxy.main import models


__all__ = (
    'ArtifactDownloadView',
)

logger = logging.getLogger(__name__)


class ArtifactDownloadView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, filename):
        try:
            filename = CollectionFilename.parse(filename)
        except ValueError:
            raise NotFound(f'Artifact "{filename}" does not exist.')

        try:
            version = models.CollectionVersion.objects.get(
                collection__namespace__name__iexact=filename.namespace,
                collection__name__iexact=filename.name,
                version__exact=filename.version,
            )
        except models.CollectionVersion.DoesNotExist:
            raise NotFound(f'Artifact "{filename}" does not exist.')

        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if user_agent.startswith('ansible-galaxy/'):
            version.collection.inc_download_count()

        ca = version.get_content_artifact()
        filename = PurePath(ca.relative_path).name

        # If artifact url is a remote URL (e.g. S3 URL) return redirect to
        # # this URL.
        artifact_file = ca.artifact.file
        storage = artifact_file.storage
        if isinstance(storage, s3boto3.S3Boto3Storage):
            return self._s3_redirect(artifact_file, filename)

        # If running in debug mode serve file directly by Django.
        if isinstance(storage, FileSystemStorage):
            return self._serve_file(artifact_file, filename)

        raise ImproperlyConfigured(
            'Only S3 and local filesystem storage backends are supported.')

    def _s3_redirect(self, artifact_file, filename):
        content_disposition = f'attachment; filename={filename}'
        parameters = {
            'ResponseContentDisposition': content_disposition
        }
        url = artifact_file.storage.url(
            artifact_file.name, parameters=parameters)
        return redirect(url)

    def _serve_file(self, artifact_file, filename):
        if not settings.DEBUG:
            logger.warning(
                f'Serving artifact "{filename}" directly by Django '
                f'application. This can affect service performance and '
                f'should not be used in production.')
        storage = artifact_file.storage
        try:
            return FileResponse(storage.open(artifact_file.path),
                                as_attachment=True, filename=filename)
        except FileNotFoundError:
            raise NotFound(f'Artifact "{filename}" does not exist.')
