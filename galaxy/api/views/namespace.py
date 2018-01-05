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

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from galaxy.accounts.models import CustomUser as User
from galaxy.main.models import Namespace, Provider, ProviderNamespace
from .base_views import ListAPIView, RetrieveUpdateDestroyAPIView
from ..serializers import NamespaceSerializer

__all__ = [
    'NamespaceList',
    'NamespaceDetail'
]

logger = logging.getLogger(__name__)


class NamespaceList(ListAPIView):
    model = Namespace
    serializer_class = NamespaceSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        errors = {}
        owners = []

        if not data.get('name'):
            errors['name'] = "Attribute 'name' is required"

        try:
            Namespace.objects.get(name__iexact=data['name'])
            errors['name'] = "A namespace with this name already exists"
        except ObjectDoesNotExist:
            pass

        if not data.get('description'):
            errors['description'] = "Attribute 'description' is required"

        if not data.get('provider_namespaces'):
            errors['provider_namespaces'] = 'A minimum of one provider namespace is required'
        elif not isinstance(data['provider_namespaces'], list):
            errors['provider_namespaces'] = 'Invalid type. Expected list'
        else:
            provider_errors = {}
            cnt = 0
            for pns in data['provider_namespaces']:
                if not isinstance(pns, dict):
                    errors['owners'] = 'Invalid type. Expected dictionary'
                    continue
                if not pns.get('name'):
                    provider_errors[cnt] = "Attribute 'name' is required"
                if not pns.get('provider'):
                    provider_errors[cnt] = "Attribute 'provider' is required"
                provider = None
                try:
                    provider = Provider.objects.get(name__iexact=pns['provider'])
                except ObjectDoesNotExist:
                    provider_errors[cnt] = "The 'provider' attribute contains an invalid provider name"
                if provider:
                    existing_namespaces = ProviderNamespace.objects.filter(provider=provider,
                                                                           name__iexact=pns['name'],
                                                                           namespace__isnull=False)
                    if len(existing_namespaces) > 0:
                        provider_errors[cnt] = 'This provider namespace is already associated with a Galaxy namespace'
                cnt += 1
            if provider_errors:
                errors['provider_namespaces'] = provider_errors

        if data.get('owners'):
            if not isinstance(data['owners'], list):
                errors['owners'] = 'Invalid type. Expected list'
            else:
                owner_errors = {}
                cnt = 0
                for owner in data.get('owners'):
                    if not isinstance(owner, dict):
                        owner_errors[cnt] = 'Invalid type. Expected dictionary'
                        continue
                    if not owner.get('id'):
                        owner_errors[cnt] = "Attribute 'id' id required"
                        continue
                    try:
                        User.objects.get(pk=owner['id'])
                    except ObjectDoesNotExist:
                        owner_errors[cnt] = "A user does not exist for this 'id'"
                        continue
                    if owner['id'] not in owners:
                        owners.append(owner['id'])
                    cnt += 1
                if owner_errors:
                    errors['owners'] = owner_errors

        if errors:
            raise ValidationError(detail=errors)

        if request.user.id not in owners:
            owners.append(request.user.id)

        namespace_attributes = {
            'name': data['name'],
            'description': data['description'],
        }
        for item in ('avatar_url', 'location', 'company', 'email', 'html_url'):
            if data.get(item):
                namespace_attributes[item] = data[item]
        try:
            namespace = Namespace.objects.create(**namespace_attributes)
            for id in owners:
                owner = User.objects.get(pk=id)
                namespace.owners.add(owner)
        except Exception as exc:
            raise APIException('Error creating namespace: {0}'.format(exc.message))

        for pns in data['provider_namespaces']:
            pns_attributes = {}
            for item in ('description', 'display_name', 'avatar_url', 'location', 'company', 'email', 'html_url',
                         'followers'):
                if pns.get(item):
                    pns_attributes[item] = pns[item]

            provider = Provider.objects.get(name__iexact=pns['provider'])
            pns_attributes['provider'] = provider
            pns_attributes['namespace'] = namespace

            try:
                ProviderNamespace.objects.update_or_create(name=pns['name'], defaults=pns_attributes)
            except Exception as exc:
                raise APIException('Error creating provider namespaces: {0}'.format(exc.message))

        serializer = self.get_serializer(instance=namespace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NamespaceDetail(RetrieveUpdateDestroyAPIView):
    model = Namespace
    serializer_class = NamespaceSerializer
