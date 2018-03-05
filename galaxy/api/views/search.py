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

import math
from collections import OrderedDict

from django.core.urlresolvers import reverse
from drf_haystack.viewsets import HaystackViewSet
from elasticsearch_dsl import Q, Search
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from galaxy.api import filters
from galaxy.api import serializers
from galaxy.api.views import base_views as base
from galaxy.main import models


__all__ = [
    'ApiV1SearchView',
    'RoleSearchView',
    'UserSearchView',
    'PlatformsSearchView',
    'CloudPlatformsSearchView',
    'TagsSearchView',
]


class ApiV1SearchView(base.APIView):
    permission_classes = (AllowAny,)
    view_name = 'Search'

    def get(self, request, *args, **kwargs):
        data = OrderedDict()
        data['platforms'] = reverse('api:platforms_search_view')
        data['cloud_platforms'] = reverse('api:cloud_platforms_search_view')
        data['roles'] = reverse('api:search-roles-list')
        data['tags'] = reverse('api:tags_search_view')
        data['users'] = reverse('api:user_search_view')
        data['top_contributors'] = reverse('api:top_contributors_list')
        return Response(data)


class RoleSearchView(HaystackViewSet):
    index_models = [models.Content]
    serializer_class = serializers.RoleSearchSerializer
    url_path = ''
    lookup_sep = ','
    filter_backends = [filters.HaystackFilter]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        print(queryset)
        instance = self.filter_queryset(queryset)
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)


class UserSearchView(base.APIView):
    def get(self, request, *args, **kwargs):
        q = None
        page = 0
        page_size = 10
        order_fields = []
        for key, value in request.GET.items():
            if key in ('username', 'content', 'autocomplete'):
                q = Q('match', username=value)
            if key == 'page':
                page = int(value) - 1 if int(value) > 0 else 0
            if key == 'page_size':
                page_size = int(value)
            if key in ('order', 'order_by'):
                order_fields = value.split(',')
        if page_size > 1000:
            page_size = 1000
        s = Search(index='galaxy_users')
        s = s.query(q) if q else s
        s = s.sort(*order_fields) if len(order_fields) > 0 else s
        s = s[page * page_size:page * page_size + page_size]
        result = s.execute()
        serializer = serializers.ElasticSearchDSLSerializer(
            result.hits, many=True)
        response = get_response(request=request, result=result,
                                view='api:user_search_view')
        response['results'] = serializer.data
        return Response(response)


class PlatformsSearchView(base.APIView):
    def get(self, request, *args, **kwargs):
        q = None
        page = 0
        page_size = 10
        order_fields = []
        for key, value in request.GET.items():
            if key == 'name':
                q = Q('match', name=value)
            if key == 'releases':
                q = Q('match', releases=value)
            if key in ('content', 'autocomplete'):
                q = Q('match', autocomplete=value)
            if key == 'page':
                page = int(value) - 1 if int(value) > 0 else 0
            if key == 'page_size':
                page_size = int(value)
            if key in ('order', 'order_by'):
                order_fields = value.split(',')
        if page_size > 1000:
            page_size = 1000
        s = Search(index='galaxy_platforms')
        s = s.query(q) if q else s
        s = s.sort(*order_fields) if len(order_fields) > 0 else s
        s = s[page * page_size:page * page_size + page_size]
        result = s.execute()
        serializer = serializers.ElasticSearchDSLSerializer(
            result.hits, many=True)
        response = get_response(request=request, result=result,
                                view='api:platforms_search_view')
        response['results'] = serializer.data
        return Response(response)


class CloudPlatformsSearchView(base.APIView):
    def get(self, request, *args, **kwargs):
        q = None
        page = 0
        page_size = 10
        order_fields = []
        for key, value in request.GET.items():
            if key == 'name':
                q = Q('match', name=value)
            if key in ('content', 'autocomplete'):
                q = Q('match', autocomplete=value)
            if key == 'page':
                page = int(value) - 1 if int(value) > 0 else 0
            if key == 'page_size':
                page_size = int(value)
            if key in ('order', 'order_by'):
                order_fields = value.split(',')
        if page_size > 1000:
            page_size = 1000
        s = Search(index='galaxy_cloud_platforms')
        s = s.query(q) if q else s
        s = s.sort(*order_fields) if len(order_fields) > 0 else s
        s = s[page * page_size:page * page_size + page_size]
        result = s.execute()
        serializer = serializers.ElasticSearchDSLSerializer(
            result.hits, many=True)
        response = get_response(request=request, result=result,
                                view='api:cloud_platforms_search_view')
        response['results'] = serializer.data
        return Response(response)


class TagsSearchView(base.APIView):
    def get(self, request, *args, **kwargs):
        q = None
        page = 0
        page_size = 10
        order_fields = []
        for key, value in request.GET.items():
            if key in ('tag', 'content', 'autocomplete'):
                q = Q('match', tag=value)
            if key == 'page':
                page = int(value) - 1 if int(value) > 0 else 0
            if key == 'page_size':
                page_size = int(value)
            if key in ('order', 'orderby'):
                order_fields = value.split(',')
        if page_size > 1000:
            page_size = 1000
        s = Search(index='galaxy_tags')
        s = s.query(q) if q else s
        s = s.sort(*order_fields) if len(order_fields) > 0 else s
        s = s[page * page_size:page * page_size + page_size]
        result = s.execute()
        serializer = serializers.ElasticSearchDSLSerializer(
            result.hits, many=True)
        response = get_response(request=request, result=result,
                                view='api:tags_search_view')
        response['results'] = serializer.data
        return Response(response)


def get_response(*args, **kwargs):
    """
    Create a response object with paging, count and
    timing attributes for search result views.
    """
    page = 0
    page_size = 10
    response = OrderedDict()

    request = kwargs.pop('request', None)
    result = kwargs.pop('result', None)
    view = kwargs.pop('view', None)

    for key, value in request.GET.items():
        if key == 'page':
            page = int(value) - 1 if int(value) > 0 else 0
        if key == 'page_size':
            page_size = int(value)
    if result:
        num_pages = int(math.ceil(result.hits.total / float(page_size)))
        cur_page = page + 1
        response['cur_page'] = cur_page
        response['num_pages'] = num_pages
        response['page_size'] = page_size

        if view:
            if num_pages > 1 and cur_page < num_pages:
                response['next_page'] = '{}?&page={}'.format(
                    reverse(view), page + 2)
            if num_pages > 1 and cur_page > 1:
                response['prev_page'] = '{}?&page={}'.format(
                    reverse(view), cur_page - 1)

        response['count'] = result.hits.total
        response['respose_time'] = result.took
        response['success'] = result.success()

    return response
