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
from rest_framework import views
from galaxy.main import models
from rest_framework import response
from galaxy.api.internal import serializers as internal_serializers
from galaxy.api import serializers as v1_serializers
from rest_framework import status


class RepoAndCollectionList(views.APIView):
    def get(self, request):
        namespace = request.GET.get('namespace', None)
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        package_type = request.GET.get('type', None)
        order = request.GET.get('order', 'name')

        if not namespace:
            return response.Response(
                {'detail': 'The namespace parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        collection_filter = {
            'namespace__name': namespace,
        }

        repo_filter = {
            'provider_namespace__namespace__name': namespace
        }

        if 'name' in request.GET:
            collection_filter['name__icontains'] = request.GET['name']
            repo_filter['name__icontains'] = request.GET['name']

        if 'description' in request.GET:
            collection_filter[
                'latest_version__metadata__description__icontaines'
            ] = request.GET['description']
            repo_filter['description__icontains'] = request.GET['description']

        # Avoid loading models if the type is set.
        if package_type == 'collection':
            repos = models.Repository.objects.none()
            repo_count = 0
        else:
            repos = models.Repository.objects.filter(
                **repo_filter).order_by(order)
            repo_count = repos.count()

        if package_type == 'repository':
            collections = models.collection.objects.none()
            collection_count = 0
        else:
            collections = models.Collection.objects.filter(
                **collection_filter).order_by(order)
            collection_count = collections.count()

        start = (page * page_size) - page_size
        end = page * page_size

        collection_results = collections[start:end]

        # If the collections fill the whole page, don't bother loading the
        # repos
        if (len(collection_results) == page_size):
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

        return(response.Response(result))
