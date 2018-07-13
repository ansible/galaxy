import base64
import json
from hashlib import sha256

import requests
from OpenSSL import crypto
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.authentication import (
    TokenAuthentication, SessionAuthentication
)
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from galaxy import constants
from galaxy.accounts.models import CustomUser as User
from galaxy.api import serializers, tasks
from galaxy.api.permissions import ModelAccessPermission
from galaxy.api.views import base_views
from galaxy.main import models


TRAVIS_STATUS_URL = "https://travis-ci.org/{user}/{repo}.svg?branch={branch}"

__all__ = [
    'NotificationSecretList',
    'NotificationSecretDetail',
    'NotificationList',
    'NotificationDetail',
]


class NotificationSecretList(base_views.ListCreateAPIView):
    """
    Integration tokens.
    """
    model = models.NotificationSecret
    serializer_class = serializers.NotificationSecretSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, ModelAccessPermission)

    def list(self, request, *args, **kwargs):
        # only list secrets belonging to the authenticated user
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        secret = request.data.get('secret', None)
        source = request.data.get('source', None)
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)

        if not secret or not source or not github_user or not github_repo:
            raise ValidationError({
                'detail': "Invalid request. "
                          "Missing one or more required values."
            })

        if source not in ['github', 'travis']:
            raise ValidationError({
                'detail': "Invalid source value. "
                          "Expecting one of: [github, travis]"
            })

        if source == 'travis':
            secret = sha256(
                github_user + '/' + github_repo + secret
            ).hexdigest()

        secret, create = models.NotificationSecret.objects.get_or_create(
            source=source,
            github_user=github_user,
            github_repo=github_repo,
            defaults={
                'owner': request.user,
                'source': source,
                'secret': secret,
                'github_user': github_user,
                'github_repo': github_repo
            }
        )

        if not create:
            msg = (
                "Duplicate key. An integration for {0} {1} {2} "
                "already exists.".format(source, github_user, github_repo)
            )
            raise ValidationError({'detail': msg})

        serializer = self.get_serializer(instance=secret)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class NotificationSecretDetail(base_views.RetrieveUpdateDestroyAPIView):
    model = models.NotificationSecret
    serializer_class = serializers.NotificationSecretSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, ModelAccessPermission,)

    def put(self, request, *args, **kwargs):
        source = request.data.get('source', None)
        secret = request.data.get('secret', None)
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)

        if not secret or not source or not github_user or not github_repo:
            raise ValidationError({
                'detail': "Invalid request. "
                          "Missing one or more required values."
            })

        if source not in ['github', 'travis']:
            raise ValidationError({
                'detail': "Invalid source value. "
                          "Expecting one of: [github, travis]"
            })

        instance = self.get_object()

        if source == 'travis':
            secret = sha256(
                github_user + '/' + github_repo + secret
            ).hexdigest()

        try:
            instance.source = source
            instance.secret = secret
            instance.github_user = github_user
            instance.github_repo = github_repo
            instance.save()
        except IntegrityError:
            msg = (
                "An integration for {0} {1} {2} already exists.".format(
                    source, github_user, github_repo)
            )
            raise ValidationError({'detail': msg})

        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, *args, **kwargs):
        obj = super(NotificationSecretDetail, self).get_object()
        obj.delete()
        return Response(dict(detail="Requested secret deleted."),
                        status=status.HTTP_202_ACCEPTED)


class NotificationList(base_views.ListCreateAPIView):
    model = models.Notification
    serializer_class = serializers.NotificationSerializer

    def post(self, request, *args, **kwargs):
        self._verify_request(request)

        github_user, github_repo = self._get_repo_info(request)
        owner = self._get_owner(github_user)
        payload = json.loads(request.POST['payload'])
        request_branch = payload['branch']
        travis_status_url = TRAVIS_STATUS_URL.format(
            user=github_user, repo=github_repo, branch=request_branch)
        committed_at = payload.get('committed_at')
        if committed_at:
            committed_at = parse_datetime(committed_at)
        else:
            committed_at = timezone.now()

        try:
            provider_ns = models.ProviderNamespace.objects.get(
                provider__name=constants.PROVIDER_GITHUB,
                name=github_user,
            )
        except models.ProviderNamespace.DoesNotExist:
            return ValidationError('Prodiver namespace "{}" not found'
                                   .format(github_user))

        notification = models.Notification(
            owner=owner,
            source='travis',
            github_branch=request_branch,
            travis_build_url=payload.get('build_url'),
            travis_status=payload.get('status_message'),
            commit_message=payload.get('message'),
            committed_at=committed_at,
            commit=payload['commit']
        )

        repository, _ = models.Repository.objects.get_or_create(
            provider_namespace=provider_ns,
            original_name=github_repo,
            defaults={
                'name': github_repo,
                'is_enabled': False,
                'travis_status_url': travis_status_url,
                'travis_build_url': payload.get('build_url'),
            })
        notification.repository = repository

        task = tasks.create_import_task(
            repository, owner,
            travis_status_url=travis_status_url,
            travis_build_url=payload.get('build_url'))
        notification.import_task = task

        notification.save()

        serializer = self.get_serializer(instance=notification)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def _verify_signature(self, signature, public_key, payload):
        """
        Convert the PEM encoded public key to a format palatable for pyOpenSSL,
        then verify the signature
        """
        pkey_public_key = crypto.load_publickey(
            crypto.FILETYPE_PEM, public_key)
        certificate = crypto.X509()
        certificate.set_pubkey(pkey_public_key)
        crypto.verify(certificate, signature, payload, 'sha1')

    def _get_repo_info(self, request):
        """Return github username and repository from request headers."""

        slug = request.META.get('HTTP_TRAVIS_REPO_SLUG')
        if not slug:
            raise ValidationError('Expected "TRAVIS_REPO_SLUG" header')
        return slug.split('/', 1)

    def _get_signature(self, request):
        """
        Extract the raw bytes of the request signature provided by travis
        """
        signature = request.META['HTTP_SIGNATURE']
        return base64.b64decode(signature)

    def _get_travis_public_key(self):
        """
        Returns the PEM encoded public key from the Travis CI /config endpoint
        """
        response = requests.get(settings.TRAVIS_CONFIG_URL, timeout=10.0)
        response.raise_for_status()
        travis_config = response.json()['config']
        return travis_config['notifications']['webhook']['public_key']

    def _get_owner(self, github_user):
        try:
            return User.objects.get(username=github_user)
        except User.DoesNotExist:
            pass

        try:
            return User.objects.get(
                username=settings.GITHUB_TASK_USERS[0])
        except User.DoesNotExist:
            raise ValidationError('Galaxy task user not found')

    def _verify_request(self, request):
        signature = self._get_signature(request)
        payload = request.POST['payload']
        try:
            public_key = self._get_travis_public_key()
        except requests.Timeout:
            # TODO(cutwater): Probably it shouldn't be "Bad request"
            raise ValidationError(
                "Timeout attempting to retrieve Travis CI public key")
        except requests.RequestException as e:
            raise ValidationError(
                "Failed to retrieve Travis CI public key. {}"
                .format(e.message)
            )
        try:
            self._verify_signature(signature, public_key, payload)
        except crypto.Error:
            # FIXME(cutwater): Raise permission denied
            raise ValidationError("Authorization failed")


class NotificationDetail(base_views.RetrieveAPIView):
    model = models.Notification
    serializer_class = serializers.NotificationSerializer
