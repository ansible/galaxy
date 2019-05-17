# (c) 2012-2019, Ansible by Red Hat
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
from rest_framework import response
from rest_framework import exceptions
from django.core import exceptions as django_exceptions

from galaxy.api import base
from galaxy.main import models
from galaxy.api.internal import serializers as internal_serializers
from galaxy.api import serializers as v1_serializers


class RepoAndCollectionList(base.APIView):
    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
        except ValueError:
            raise exceptions.ValidationError(
                detail='Pagination values must be numbers')

        namespace = request.GET.get('namespace', None)
        package_type = request.GET.get('type', None)
        order = request.GET.get('order', 'name')

        self._validate_order(order)

        if not namespace:
            raise exceptions.ValidationError(
                detail='The namespace parameter is required')

        collection_filters = {
            'namespace__name': namespace,
        }

        repo_filters = {
            'provider_namespace__namespace__name': namespace
        }

        if 'name' in request.GET:
            collection_filters['name__icontains'] = request.GET['name']
            repo_filters['name__icontains'] = request.GET['name']

        # Avoid loading models if the type is set.
        if package_type == 'collection':
            repos = models.Repository.objects.none()
            repo_count = 0
        else:
            repos = models.Repository.objects.filter(
                **repo_filters).order_by(order)
            repo_count = repos.count()

        if package_type == 'repository':
            collections = models.Collection.objects.none()
            collection_count = 0
        else:
            collections = models.Collection.objects.filter(
                **collection_filters).order_by(order)
            collection_count = collections.count()

        start = (page * page_size) - page_size
        end = page * page_size

        collection_results = collections[start:end]

        # If the collections fill the whole page, don't bother loading the
        # repos
        if len(collection_results) == page_size:
            repo_results = []
        else:
            # Django gets cranky if you try to slice a queryset with a negative
            # index
            r_start = max(0, start - collection_count)

            repo_results = repos[r_start:end-collection_count]

        result = {
            'collection':
                {
                    'count': collection_count,
                    'results': internal_serializers.CollectionListSerializer(
                        collection_results,
                        many=True
                    ).data,
                },
            'repository':
                {
                    'count': repo_count,
                    'results': v1_serializers.RepositorySerializer(
                        repo_results,
                        many=True,
                    ).data,
                }
        }

        return response.Response(result)

    def _validate_order(self, order):
        allowed_orders = ['download_count', 'name', '-download_count', '-name']
        if order not in allowed_orders:
            raise exceptions.ValidationError(
                detail='Order must be one of {fields}'.format(
                    fields=str(allowed_orders)
                )
            )


class CombinedDetail(base.APIView):
    '''
    This is intendended to provide all of the information for the content
    detail pages. For repos, it returns the repository, namespace and list of
    content items.

    For collections it returns a collection object
    '''
    def get(self, request):
        namespace = request.GET.get('namespace', None)
        name = request.GET.get('name', None)

        if not name or not namespace:
            raise exceptions.ValidationError(
                detail='namespace and name parameters are required')

        try:
            repo = models.Repository.objects.get(
                provider_namespace__namespace__name=namespace,
                name=name
            )
            namespace_obj = models.Namespace.objects.get(name=namespace)
            content = models.Content.objects.filter(
                repository__name__iexact=name,
                repository__provider_namespace__namespace__name__iexact=namespace # noqa
            )

            data = {
                'repository': v1_serializers.RepositorySerializer(repo).data,
                'namespace': v1_serializers.NamespaceSerializer(
                    namespace_obj).data,
                'content': v1_serializers.ContentSerializer(
                    content, many=True).data
            }
            return response.Response({'type': 'repository', 'data': data})
        except django_exceptions.ObjectDoesNotExist:
            pass

        try:
            collection = models.Collection.objects.get(
                namespace__name=namespace,
                name=name
            )
            data = {
                'collection': internal_serializers.CollectionDetailSerializer(
                    collection).data
            }
            return response.Response({'type': 'collection', 'data': data})
        except django_exceptions.ObjectDoesNotExist:
            raise exceptions.NotFound(
                detail="No collection or repository could be found " +
                "matching the name {}.{}".format(namespace, name)
            )
