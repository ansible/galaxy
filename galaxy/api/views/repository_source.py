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

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from django.core.exceptions import ObjectDoesNotExist

from galaxy.main.models import Provider, ProviderNamespace, Repository
from .base_views import ListAPIView
from ..githubapi import GithubAPI
from ..serializers import RepositorySourceSerializer


__all__ = [
    'RepositorySourceList',
    'RepositorySourceDetail',
]

logger = logging.getLogger(__name__)


class RepositorySourceList(ListAPIView):
    """Repositories available for a given provider and namespace."""
    model = Repository
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RepositorySourceSerializer

    def get(self, request, *args, **kwargs):
        # Return a list of repositories from the provider for a given namespace
        request_provider = kwargs.get('provider_name')
        request_namespace = kwargs.get('provider_namespace')
        repos = []
        try:
            provider = Provider.objects.get(
                name__iexact=request_provider.lower(), active=True
            )
        except ObjectDoesNotExist:
            raise APIException("Invalid provider {0}".format(request_provider))

        try:
            provider_namespace = ProviderNamespace.objects.get(
                provider=provider, name__iexact=request_namespace
            )
        except ObjectDoesNotExist:
            provider_namespace = None

        if provider.name.lower() == 'github':
            repos = GithubAPI(user=request.user).get_namespace_repositories(
                request_namespace
            )

        for repo in repos:
            repo['source_namespace'] = request_namespace
            repo['provider_namespace'] = None
            repo['provider_namespace_url'] = None
            repo['namespace'] = None
            repo['namespace_url'] = None
            repo['repository'] = None
            repo['repository_url'] = None

            repo['provider'] = {
                'id': provider.pk,
                'name': provider.name.lower()
            }

            if provider_namespace:
                try:
                    repository_obj = Repository.objects.get(
                        provider_namespace=provider_namespace,
                        original_name=repo['name']
                    )
                except ObjectDoesNotExist:
                    repository_obj = None

                if repository_obj:
                    repo['provider_namespace'] = {
                        'id': provider_namespace.pk,
                        'name': provider_namespace.name
                    }
                    repo[
                        'provider_namespace_url'
                    ] = provider_namespace.get_absolute_url()
                    repo['namespace'] = {
                        'id': provider_namespace.namespace.pk,
                        'name': provider_namespace.namespace.name
                    }
                    repo[
                        'namespace_url'
                    ] = provider_namespace.namespace.get_absolute_url()
                    repo['repository'] = {
                        'id': repository_obj.pk,
                        'name': repository_obj.name,
                        'original_name': repository_obj.original_name
                    }
                    repo['repository_url'] = repository_obj.get_absolute_url()

        serializer = self.get_serializer(repos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RepositorySourceDetail(ListAPIView):
    """ Details for a specific repo """
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RepositorySourceSerializer

    def get(self, request, *args, **kwargs):
        # Return a list of repositories from the provider for a given namespace
        request_provider = kwargs.get('provider_name')
        request_namespace = kwargs.get('provider_namespace')
        request_repo = kwargs.get('repo_name')
        repo = {}

        try:
            provider = Provider.objects.get(
                name__iexact=request_provider.lower(), active=True
            )
        except ObjectDoesNotExist:
            raise APIException("Invalid provider {0}".format(request_provider))

        try:
            provider_namespace = ProviderNamespace.objects.get(
                provider=provider, name__iexact=request_namespace
            )
        except ObjectDoesNotExist:
            provider_namespace = None

        if provider.name.lower() == 'github':
            repos = GithubAPI(user=request.user).get_namespace_repositories(
                request_namespace, name=request_repo
            )
            if len(repos):
                repo = repos[0]

        if repo.get('name'):
            repo['source_namespace'] = request_namespace
            repo['provider_namespace'] = None
            repo['provider_namespace_url'] = None
            repo['namespace'] = None
            repo['namespace_url'] = None
            repo['repository'] = None
            repo['repository_url'] = None

            repo['provider'] = {
                'id': provider.pk,
                'name': provider.name.lower()
            }

            if provider_namespace:
                try:
                    repository_obj = Repository.objects.get(
                        provider_namespace=provider_namespace,
                        original_name=repo['name']
                    )
                except ObjectDoesNotExist:
                    repository_obj = None

                if repository_obj:
                    repo['provider_namespace'] = {
                        'id': provider_namespace.pk,
                        'name': provider_namespace.name
                    }
                    repo[
                        'provider_namespace_url'
                    ] = provider_namespace.get_absolute_url()
                    repo['namespace'] = {
                        'id': provider_namespace.namespace.pk,
                        'name': provider_namespace.namespace.name
                    }
                    repo[
                        'namespace_url'
                    ] = provider_namespace.namespace.get_absolute_url()
                    repo['repository'] = {
                        'id': repository_obj.pk,
                        'name': repository_obj.name,
                        'original_name': repository_obj.original_name
                    }
                    repo['repository_url'] = repository_obj.get_absolute_url()

        serializer = self.get_serializer(repo, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
