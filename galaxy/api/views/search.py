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

from collections import OrderedDict

from django.core.urlresolvers import reverse
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status as http_status

from galaxy.api.views import base_views as base


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
        # TODO(cutwater): Remove out of search
        data['top_contributors'] = reverse('api:top_contributors_list')
        return Response(data)


class RoleSearchView(base.APIView):
    def get(self, request, format=None):
        return Response({
            'error': 'Not implemented yet'
        }, status=http_status.HTTP_501_NOT_IMPLEMENTED)


class UserSearchView(base.APIView):
    def get(self, request, format=None):
        return Response({
            'error': 'Not implemented yet'
        }, status=http_status.HTTP_501_NOT_IMPLEMENTED)


class PlatformsSearchView(base.APIView):
    def get(self, request, format=None):
        return Response({
            'error': 'Not implemented yet'
        }, status=http_status.HTTP_501_NOT_IMPLEMENTED)


class CloudPlatformsSearchView(base.APIView):
    def get(self, request, format=None):
        return Response({
            'error': 'Not implemented yet'
        }, status=http_status.HTTP_501_NOT_IMPLEMENTED)


class TagsSearchView(base.APIView):
    def get(self, request, format=None):
        return Response({
            'error': 'Not implemented yet'
        }, status=http_status.HTTP_501_NOT_IMPLEMENTED)
