# (c) 2012-2018, Ansible by Red Hat
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
import re

from django.core.exceptions import ObjectDoesNotExist

# filter backends
from rest_framework.filters import SearchFilter
from ..filters import FieldLookupBackend, OrderByBackend

from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from galaxy.accounts.models import CustomUser as User
from galaxy.main.models import Repository, ProviderNamespace
from .base_views import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from ..serializers import RepositorySerializer
from ..githubapi import GithubAPI

__all__ = [
    'RepositoryList',
    'RepositoryDetail'
]

logger = logging.getLogger(__name__)


def get_repo(provider_namespace, user, repo_name):
    repo = {}
    if provider_namespace.provider.name.lower() == 'github':
        # Check that the user has access to the requested repo
        repos = GithubAPI(user=user).get_namespace_repositories(provider_namespace.name, name=repo_name)
        if repos:
            repo = repos[0]
    return repo


def check_name(name):
    if not name:
        raise ValidationError(detail={'name': 'Name is required'})

    if not re.match('^[\w-]+$', name):
        # Allow only names containing word chars and '-'
        raise ValidationError(detail={
            'name': 'Name contains invalid characters. Must match [A-Za-z0-9-_].'
        })


GITHUB_REPO_FIELDS = [
    'commit',
    'commit_message',
    'commit_url',
    'commit_created',
    'stargazers_count',
    'watchers_count',
    'forks_count',
    'open_issues_count'
]


class RepositoryList(ListCreateAPIView):
    model = Repository
    serializer_class = RepositorySerializer
    filter_backends = (FieldLookupBackend, SearchFilter, OrderByBackend)

    def post(self, request, *args, **kwargs):
        data = request.data
        owners = data.pop('owners', [])
        if not data.get('provider_namespace'):
            raise ValidationError(detail={'provider_namespace': 'Value required'})

        check_name(data.get('name'))

        try:
            provider_namespace = ProviderNamespace.objects.get(pk=data['provider_namespace'])
        except ObjectDoesNotExist:
            raise ValidationError(detail={'provider_namespace': 'Invalid value'})

        original_name = data.get('original_name', data['name'])

        data['name'] = data['name'].lower()

        repo = get_repo(provider_namespace, request.user, original_name)
        if not repo:
            raise APIException("User does not have access to {0}/{1} in GitHub".format(provider_namespace.name,
                                                                                       original_name))
        for field in GITHUB_REPO_FIELDS:
            data[field] = repo[field]

        if not data.get('original_name'):
            data['original_name'] = original_name

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        data['provider_namespace'] = provider_namespace
        try:
            repository = Repository.objects.create(**data)
        except Exception as exc:
            raise APIException('Error creating repository: {0}'.format(exc.message))

        for owner_pk in owners:
            try:
                owner = User.objects.get(pk=owner_pk)
            except ObjectDoesNotExist:
                pass
            else:
                owner.repositories.add(repository)

        serializer = self.get_serializer(repository)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RepositoryDetail(RetrieveUpdateDestroyAPIView):
    model = Repository
    serializer_class = RepositorySerializer
    filter_backends = (FieldLookupBackend, SearchFilter, OrderByBackend)

    def update(self, request, *args, **kwargs):
        data = request.data
        owners = data.pop('owners', [])
        instance = self.get_object()

        if data.get('provider_namespace'):
            try:
                provider_namespace = ProviderNamespace.objects.get(pk=data['provider_namespace'])
            except ObjectDoesNotExist:
                raise ValidationError(detail={'provider_namespace': 'Invalid value'})
        else:
            provider_namespace = instance.provider_namespace

        check_name(data.get('name'))

        original_name = data.get('original_name', instance.original_name)

        repo = get_repo(provider_namespace, request.user, original_name)
        if not repo:
            raise APIException(
                "User does not have access to {0}/{1} in GitHub".format(provider_namespace.name,
                                                                        original_name)
            )

        for field in GITHUB_REPO_FIELDS:
            data[field] = repo[field]

        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)

        try:
            Repository.objects.filter(pk=instance.pk).update(**data)
        except Exception as exc:
            raise APIException('Error updating repository: {0}'.format(exc.message))

        instance = self.get_object()

        for owner_pk in owners:
            try:
                owner = User.objects.get(pk=owner_pk)
            except ObjectDoesNotExist:
                pass
            else:
                owner.repositories.add(instance)

        if not request.user.repositories.filter(pk=instance.pk):
            request.user.repositories.add(instance)

        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        repo = get_repo(instance.provider_namespace, request.user, instance.original_name)
        if not repo:
            raise APIException(
                "User does not have access to {0}/{1} in GitHub".format(instance.provider_namespace.name,
                                                                        instance.original_name)
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
