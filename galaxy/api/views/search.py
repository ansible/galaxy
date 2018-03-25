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

import operator
from collections import OrderedDict

import six
from django.db.models import Func, F, Value, ExpressionWrapper
from django.db.models import fields as db_fields
from django.core.urlresolvers import reverse
from django.contrib.postgres import search as psql_search

from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from galaxy.accounts import models as auth_models
from galaxy.api import filters
from galaxy.api import serializers
from galaxy.api.views import base_views as base
from galaxy.main import models
from galaxy.main import constants

__all__ = [
    'ApiV1SearchView',
    'ContentSearchView',
    'RoleSearchView',
    'UserSearchView',
    'PlatformsSearchView',
    'CloudPlatformsSearchView',
    'TagsSearchView',
]


RANK_FUNCTION = 'ts_rank'
RANK_NORMALIZATION = 32

DOWNLOAD_RANK_MULTIPLIER = 0.4


class ApiV1SearchView(base.APIView):
    permission_classes = (AllowAny,)
    view_name = 'Search'

    def get(self, request, *args, **kwargs):
        data = OrderedDict()
        data['cloud_platforms'] = reverse('api:cloud_platforms_search_view')
        data['content'] = reverse('api:content_search_view')
        data['platforms'] = reverse('api:platforms_search_view')
        data['roles'] = reverse('api:roles_search_view')
        data['tags'] = reverse('api:tags_search_view')
        data['top_contributors'] = reverse('api:top_contributors_list')
        data['users'] = reverse('api:user_search_view')
        return Response(data)


class ContentSearchView(base.ListAPIView):

    serializer_class = serializers.RoleSearchSerializer
    filter_backends = [filters.OrderByFilter]

    def get_queryset(self):
        role_type = models.ContentType.get(constants.ContentType.ROLE)
        return (models.Content.objects.distinct()
                .filter(content_type=role_type))

    # TODO(cutwater): Use serializer to parse request arguments
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Content type
        content_type = request.GET.get('content_type', '')
        queryset = self.add_content_type(queryset, content_type)

        # Platforms
        platforms = request.GET.get('platforms', '').split()
        queryset = self.add_platforms_filter(queryset, platforms)

        # Cloud platforms
        cloud_platforms = request.GET.get('cloud_platforms', '').split()
        queryset = self.add_cloud_platforms_filter(queryset, cloud_platforms)

        # Namespaces
        namespaces = request.GET.get('namespaces', '').split()
        queryset = self.add_namespaces_filter(queryset, namespaces)

        # Tags
        tags = request.GET.get('tags', '').split()
        queryset = self.add_tags_filter(queryset, tags)

        # Keywords
        keywords = request.GET.get('keywords', '').split()
        queryset = self.add_keywords_filter(queryset, keywords)

        queryset = self.add_relevance(queryset)

        return self.make_response(queryset)

    @staticmethod
    def add_relevance(queryset):
        download_count_ln_expr = Func(F('download_count') + 1, function='ln')
        download_rank_expr = (
            F('download_count_ln')
            / (1 + F('download_count_ln'))
            * DOWNLOAD_RANK_MULTIPLIER
        )
        relevance_expr = ExpressionWrapper(
            F('search_rank') + F('download_rank'),
            output_field=db_fields.FloatField())

        return queryset.annotate(
            download_count_ln=download_count_ln_expr,
            download_rank=ExpressionWrapper(
                download_rank_expr,
                output_field=db_fields.FloatField()),
            relevance=relevance_expr,
        )

    @staticmethod
    def add_content_type(queryset, content_type):
        if not content_type:
            return queryset
        content_type = models.ContentType.get(content_type)
        return queryset.filter(content_type=content_type)

    @staticmethod
    def add_tags_filter(queryset, tags):
        if not tags:
            return queryset
        return queryset.filter(
            tags__in=models.Tag.objects.filter(name__in=tags))

    @staticmethod
    def add_namespaces_filter(queryset, namespaces):
        if not namespaces:
            return queryset
        return queryset.filter(namespace__name__in=namespaces)

    @staticmethod
    def add_platforms_filter(queryset, platforms):
        if not platforms:
            return queryset
        return queryset.filter(
            platforms__in=models.Platform.objects.filter(name__in=platforms))

    @staticmethod
    def add_cloud_platforms_filter(queryset, cloud_platforms):
        if not cloud_platforms:
            return queryset
        return queryset.filter(
            cloud_platforms__in=models.CloudPlatform.objects.filter(
                name__in=cloud_platforms))

    @staticmethod
    def add_keywords_filter(queryset, keywords):
        if not keywords:
            return queryset.annotate(
                search_rank=Value(0.0, output_field=db_fields.FloatField()))

        tsquery = six.moves.reduce(
            operator.and_,
            (psql_search.SearchQuery(kw) for kw in keywords))

        search_rank_fn = Func(
            F('search_vector'), tsquery, RANK_NORMALIZATION,
            function=RANK_FUNCTION, output_field=db_fields.FloatField())
        return (queryset.annotate(search_rank=search_rank_fn)
                .filter(search_vector=tsquery))


class RoleSearchView(ContentSearchView):
    def get_queryset(self):
        queryset = super(RoleSearchView, self).get_queryset()
        role_type = models.ContentType.get(constants.ContentType.ROLE)
        return queryset.filter(content_type=role_type)


# FIXME(cutwater): Keeping views compatible with ELK based.
# Refactor request parameters parsing
class UserSearchView(base.ListAPIView):

    model = auth_models.CustomUser
    serializer_class = serializers.UserListSerializer
    filter_backends = [filters.OrderByFilter]

    def list(self, request, *args, **kwargs):
        search_query = None
        for key, value in request.GET.items():
            if key in ('username', 'content', 'autocomplete'):
                search_query = value

        queryset = self.filter_queryset(self.get_queryset())
        if search_query:
            queryset.filter(username__istartswith=search_query)
        return self.make_response(queryset)


class PlatformsSearchView(base.ListAPIView):

    model = models.Platform
    serializer_class = serializers.PlatformSerializer
    filter_backends = [filters.OrderByFilter]

    def list(self, request, *args, **kwargs):
        name = None
        releases = None
        autocomplete = None

        for key, value in request.GET.items():
            if key == 'name':
                name = value
            elif key == 'releases':
                releases = value.split()
            elif key in ('content', 'autocomplete'):
                autocomplete = value

        queryset = self.filter_queryset(self.get_queryset())
        print(type(queryset), str(queryset.query))
        if name:
            queryset = queryset.filter(name=name)
        if releases:
            queryset = queryset.filter(release__in=releases)
        if autocomplete:
            where_clause = '''
                to_tsvector(
                    name || ' ' || release || ' ' || coalesce(alias, ''))
                @@ to_tsquery(quote_literal(%s) || ':*')
            '''
            queryset = queryset.extra(where=[where_clause],
                                      params=[autocomplete])
        print(queryset.query)
        return self.make_response(queryset)


class CloudPlatformsSearchView(base.ListAPIView):

    model = models.CloudPlatform
    serializer_class = serializers.CloudPlatformSerializer
    filter_backends = [filters.OrderByFilter]

    def list(self, request, *args, **kwargs):
        match_query = None
        search_query = None
        for key, value in request.GET.items():
            if key == 'name':
                match_query = value
            elif key in ('content', 'autocomplete'):
                search_query = value

        queryset = self.filter_queryset(self.get_queryset())
        if match_query:
            queryset = queryset.filter(name=match_query)
        if search_query:
            queryset = queryset.filter(name__istartswith=search_query)
        return self.make_response(queryset)


class TagsSearchView(base.ListAPIView):

    model = models.Tag
    serializer_class = serializers.TagSerializer
    filter_backends = [filters.OrderByFilter]

    def list(self, request, *args, **kwargs):
        search_query = None
        for key, value in request.GET.items():
            if key in ('tag', 'content', 'autocomplete'):
                search_query = value

        queryset = self.filter_queryset(self.get_queryset())
        if search_query:
            queryset.filter(name_istartswith=search_query)
        return self.make_response(queryset)
