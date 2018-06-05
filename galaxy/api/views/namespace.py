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
from rest_framework.exceptions import ValidationError, APIException, PermissionDenied
from rest_framework.response import Response

from galaxy.accounts.models import CustomUser as User
from galaxy.api import serializers
from galaxy.main import models
from . import base_views

__all__ = [
    'NamespaceList',
    'NamespaceDetail',
    'NamespaceProviderNamespacesList',
    'NamespaceProviderNamespacesList',
    'NamespaceContentList',
    'NamespaceOwnersList',
]

logger = logging.getLogger(__name__)


def check_basic(data, errors):
    if not data.get('name'):
        errors['name'] = "Attribute 'name' is required"
    elif not re.match('^[\w-]+$', data['name']):
        # Allow only names containing word chars and '-'
        errors['name'] = "Name can only contain [A-Za-z0-9-_]"


def check_owners(data_owners):
    if not isinstance(data_owners, list):
        errors = 'Invalid type. Expected list'
        return errors, []

    owners = []
    errors = {}
    for i in range(0, len(data_owners)):
        owner = data_owners[i]
        if not isinstance(owner, dict):
            errors[i] = 'Invalid type. Expected dictionary'
            continue
        if not owner.get('id'):
            errors[i] = "Attribute 'id' id required"
            continue
        try:
            User.objects.get(pk=owner['id'])
        except ObjectDoesNotExist:
            errors[i] = "A user does not exist for this 'id'"
            continue
        if owner['id'] not in owners:
            owners.append(owner['id'])
    return errors, owners


def check_providers(data_providers, parent=None):
    errors = {}

    if not isinstance(data_providers, list):
        return 'Invalid type. Expected list.'

    for i in range(0, len(data_providers)):
        pns = data_providers[i]
        if not isinstance(pns, dict):
            errors[i] = 'Invalid type. Expected dictionary'
            continue
        if not pns.get('name'):
            errors[i] = "Attribute 'name' is required"
            continue
        if not pns.get('provider'):
            errors[i] = "Attribute 'provider' is required"
            continue
        try:
            provider = models.Provider.objects.get(pk=pns['provider'])
        except ObjectDoesNotExist:
            errors[i] = "The 'provider' attribute contains an invalid provider"
            continue
        if provider:
            existing_namespaces = models.ProviderNamespace.objects.filter(
                provider=provider,
                name__iexact=pns['name'].lower(),
                namespace__isnull=False)
            if parent:
                existing_namespaces = existing_namespaces.exclude(namespace=parent)
            if existing_namespaces:
                errors[i] = 'This provider namespace is already associated with a Galaxy namespace'
    return errors


def update_provider_namespaces(namespace, provider_namespaces):
    # Update provider namespaces in the list
    for pns in provider_namespaces:
        pns_attributes = {}
        for item in ('display_name', 'avatar_url', 'location', 'company', 'email', 'html_url',
                     'followers'):
            if item in pns:
                pns_attributes[item] = pns[item]

        pns_attributes['description'] = pns['description'] if pns.get('description') is not None else ''

        try:
            provider = models.Provider.objects.get(pk=pns['provider'])
        except ObjectDoesNotExist:
            pass
        else:
            pns_attributes['provider'] = provider
            pns_attributes['namespace'] = namespace

            try:
                pns_obj, _ = models.ProviderNamespace.objects.update_or_create(name=pns['name'],
                                                                               defaults=pns_attributes)
                pns['id'] = pns_obj.pk
            except Exception as exc:
                raise APIException(
                    'Error creating or updating provider namespaces: {}'
                    .format(exc.message)
                )
    # Disassociate provider namespaces not in the list
    for id in [obj.pk for obj in models.ProviderNamespace.objects.filter(namespace=namespace)]:
        found = False
        for pns in provider_namespaces:
            if pns['id'] == id:
                found = True
                break
        if not found:
            # The provider namespace is no longer associated with the Galaxy namespace
            try:
                obj = models.ProviderNamespace.objects.get(pk=id)
            except ObjectDoesNotExist as exc:
                raise
            else:
                obj.namespace = None
                obj.save()


def update_owners(instance, owners):
    for owner_pk in owners:
        # add new owners
        if not instance.owners.filter(pk=owner_pk):
            try:
                owner = User.objects.get(pk=owner_pk)
            except ObjectDoesNotExist:
                pass
            else:
                instance.owners.add(owner)

    for owner in [o for o in instance.owners.all() if o.pk not in owners]:
        # remove owners not in request owners
        instance.owners.remove(owner)


class NamespaceList(base_views.ListCreateAPIView):
    model = models.Namespace
    serializer_class = serializers.NamespaceSerializer
    filter_backends = (FieldLookupBackend, SearchFilter, OrderByBackend)  # excludes ActiveOnly

    def post(self, request, *args, **kwargs):
        data = request.data
        errors = {}
        owners = []

        check_basic(data, errors)

        if data.get('name'):
            try:
                models.Namespace.objects.get(name__iexact=data['name'].lower())
                errors['name'] = "A namespace with this name already exists"
            except ObjectDoesNotExist:
                pass

        if not request.user.is_staff:
            if not data.get('provider_namespaces'):
                errors['provider_namespaces'] = 'A minimum of one provider namespace is required'
            else:
                provider_errors = check_providers(data['provider_namespaces'])
                if provider_errors:
                    errors['provider_namespaces'] = provider_errors

        if data.get('owners'):
            owner_errors, owners = check_owners(data['owners'])
            if owner_errors:
                errors['owners'] = owner_errors

        if errors:
            raise ValidationError(detail=errors)

        if not request.user.is_staff and request.user.pk not in owners:
            owners.append(request.user.id)

        namespace_attributes = {
            'name': data['name'],
            'description': data['description'] if data.get('description') is not None else ''
        }
        for item in ('avatar_url', 'location', 'company', 'email', 'html_url', 'is_vendor'):
            if item in data:
                namespace_attributes[item] = data[item]
        try:
            namespace = models.Namespace.objects.create(**namespace_attributes)
        except Exception as exc:
            raise APIException('Error creating namespace: {0}'.format(exc.message))

        update_owners(namespace, owners)
        update_provider_namespaces(namespace, data['provider_namespaces'])

        serializer = self.get_serializer(instance=namespace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NamespaceDetail(base_views.RetrieveUpdateDestroyAPIView):
    model = models.Namespace
    serializer_class = serializers.NamespaceSerializer
    filter_backends = (FieldLookupBackend, SearchFilter, OrderByBackend)  # excludes ActiveOnly

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        errors = {}
        owners = []

        check_basic(data, errors)

        if data.get('provider_namespaces'):
            provider_errors = check_providers(data['provider_namespaces'], parent=instance)
            if provider_errors:
                errors['provider_namespaces'] = provider_errors

        if data.get('owners'):
            owner_errors, owners = check_owners(data['owners'])
            if owner_errors:
                errors['owners'] = owner_errors

        if errors:
            raise ValidationError(detail=errors)

        if not request.user.is_staff and request.user.pk not in owners:
            raise PermissionDenied("User does not have access to Namespace {0}".format(
                data.get('name', '')))

        if data.get('owners'):
            update_owners(instance, owners)

        for item in ('name', 'description', 'avatar_url', 'location', 'company', 'email',
                     'html_url', 'active', 'is_vendor'):
            if item in data:
                setattr(instance, item, data[item])
        instance.save()

        if 'provider_namespaces' in data:
            update_provider_namespaces(instance, data['provider_namespaces'])

        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NamespaceProviderNamespacesList(base_views.SubListAPIView):
    view_name = "Namespace Provider Namespaces"
    model = models.ProviderNamespace
    serializer_class = serializers.ProviderNamespaceSerializer
    parent_model = models.Namespace
    relationship = "provider_namespaces"


class NamespaceContentList(base_views.SubListAPIView):
    view_name = "Namespace Content"
    model = models.Content
    serializer_class = serializers.ContentSerializer
    parent_model = models.Namespace
    relationship = "content_objects"


class NamespaceOwnersList(base_views.SubListAPIView):
    view_name = "Namespace Owners"
    model = User
    serializer_class = serializers.UserListSerializer
    parent_model = models.Namespace
    relationship = "owners"
