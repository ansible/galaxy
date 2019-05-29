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

from rest_framework.response import Response

from galaxy.api import base
from galaxy.api import exceptions
from galaxy.api import serializers as serializers_v1
from galaxy.api.internal import serializers as serializers_int
from galaxy.api.internal.search import CollectionSearch, ContentSearch
from galaxy.main import models


__all__ = (
    'SearchView',
)

CONTENT_ONLY_FILTERS = [
    'platforms',
    'cloud_platforms',
]

ALLOWED_CONTENT_TYPES = [
    'collection',
    'role',
    None
]


def _ensure_positive_int(string, field, cutoff=None):
    msg = f'{field} must be a positive integer'
    try:
        value = int(string)
    except ValueError:
        raise exceptions.ValidationError(detail=msg)
    if value < 0:
        raise exceptions.ValidationError(detail=msg)
    if cutoff is not None:
        return min(value, cutoff)
    return value


# TODO(cutwater): Lazy pagination
# TODO(cutwater): Implement autocomplete views
class SearchView(base.APIView):

    ordering_param = 'order_by'
    allowed_ordering = (
        'relevance',
        'download_count',
        'qualname',
        'name',
    )
    default_ordering = '-relevance'

    page_size = 10
    max_page_size = 100

    def get(self, request):
        page = self.get_page(request)
        page_size = self.get_page_size(request)
        order_by, order = self.get_order_by(request)
        format_type = self.get_format_type(request)
        filters = self._parse_query_params(request.query_params)

        start = page_size * (page - 1)
        end = page_size * page

        # Collections
        if format_type == 'role' \
                or any(filters[k] for k in CONTENT_ONLY_FILTERS):
            collections_count = 0
            collections = []
        else:
            collection_search = CollectionSearch(filters, order_by, order)
            collections_count = collection_search.count()
            collections = collection_search.search()[start:end]
            # TODO(cutwater): This function should be refactored in order
            #  to annotate collection objects retrieved withing search class.
            #  However due to initial design search() function returns
            #  a queryset, while pagination is performed outside.
            #  This makes injecting content_match currently impossible.
            collection_search._add_content_match(collections)

        # Contents
        if format_type == 'collection':
            content_count = 0
            contents = []
        else:
            content_search = ContentSearch(filters, order_by, order)
            content_count = content_search.count()
            if len(collections) >= page_size:
                contents = models.Content.objects.none()
            else:
                c_start = max(0, start - collections_count)
                c_end = end - collections_count
                contents = content_search.search()[c_start:c_end]

        result = {
            'collection': {
                'count': collections_count,
                'results': serializers_int.CollectionSearchSerializer(
                    collections, many=True).data
            },
            'content': {
                'count': content_count,
                'results': serializers_v1.RoleSearchSerializer(
                    contents, many=True).data,
            },
        }

        return Response(result)

    def get_page(self, request):
        return _ensure_positive_int(
            request.query_params.get('page', 1), 'page')

    def get_page_size(self, request):
        return _ensure_positive_int(
            request.query_params.get('page_size', self.page_size), 'page_size',
            self.max_page_size)

    def get_order_by(self, request):
        param = request.query_params.get(
            self.ordering_param, self.default_ordering)
        order = 'asc'
        if param.startswith('-'):
            order = 'desc'
            param = param[1:]
        if param not in self.allowed_ordering:
            raise exceptions.ValidationError(
                f'{repr(param)} is not a valid ordering parameter value.')
        return param, order

    def get_format_type(self, request):
        format = request.query_params.get('type', None)
        if format:
            format = format.lower()
        if format not in ALLOWED_CONTENT_TYPES:
            raise exceptions.ValidationError(
                f'{repr(format)} is not a valid format type.')

        return format

    @staticmethod
    def _parse_query_params(params):
        params_serializer = serializers_int.SearchRequestSerializer(
            data=params)
        params_serializer.is_valid(raise_exception=True)
        return params_serializer.validated_data
