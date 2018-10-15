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

from django.core.exceptions import ObjectDoesNotExist

from galaxy.main.models import Provider, ProviderNamespace
from .base_views import ListAPIView
from ..githubapi import GithubAPI
from ..serializers import ProviderSourceSerializer


__all__ = ['ProviderSourceList']

logger = logging.getLogger(__name__)


class ProviderSourceList(ListAPIView):
    """User namespaces available within each active provider."""

    model = ProviderNamespace
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ProviderSourceSerializer

    def get(self, request, *args, **kwargs):
        """
        Return a list of namespaces from all providers
        for the requesting user.
        """
        sources = []
        for provider in Provider.objects.filter(active=True):
            if provider.name.lower() == 'github':
                sources += GithubAPI(user=request.user).user_namespaces()
                for source in sources:
                    source['provider'] = {
                        'id': provider.pk,
                        'name': provider.name,
                    }
                    try:
                        provider_namespace = ProviderNamespace.objects.get(
                            provider=provider, name=source['name']
                        )
                        source['provider_namespace'] = {
                            'id': provider_namespace.id,
                            'name': provider_namespace.name.lower(),
                        }
                        source[
                            'provider_namespace_url'
                        ] = provider_namespace.get_absolute_url()
                    except ObjectDoesNotExist:
                        provider_namespace = None
                        source['provider_namespace'] = None
                        source['provider_namespace_url'] = None

                    if provider_namespace and provider_namespace.namespace:
                        source['namespace'] = {
                            'id': provider_namespace.namespace.pk,
                            'name': provider_namespace.namespace.name,
                        }
                        source[
                            'namespace_url'
                        ] = provider_namespace.namespace.get_absolute_url()
                    else:
                        source['namespace'] = None
                        source['namespace_url'] = None

        serializer = self.get_serializer(sources, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
