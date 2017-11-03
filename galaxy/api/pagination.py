# (c) 2012-2016, Ansible by Red Hat
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

# Django REST Framework
from rest_framework import serializers, pagination
from rest_framework.templatetags.rest_framework import replace_query_param


class NextPageField(pagination.NextPageField):
    '''Pagination field to output URL path.'''

    def to_representation(self, value):
        if not value.has_next():
            return None
        page = value.next_page_number()
        request = self.context.get('request')
        url = request and request.get_full_path() or ''
        # remove /api/v1 so ansible-galaxy pagination works
        url = url.replace('/api/v1', '')
        return replace_query_param(url, self.page_field, page)


class PreviousPageField(pagination.NextPageField):
    '''Pagination field to output URL path.'''

    def to_representation(self, value):
        if not value.has_previous():
            return None
        page = value.previous_page_number()
        request = self.context.get('request')
        url = request and request.get_full_path() or ''
        # remove /api/v1 so ansible-galaxy pagination works
        url = url.replace('/api/v1', '')
        return replace_query_param(url, self.page_field, page)


class NextLinkField(pagination.NextPageField):
    '''Pagination field to output URL path.'''

    def to_representation(self, value):
        if not value.has_next():
            return None
        page = value.next_page_number()
        request = self.context.get('request')
        url = request and request.get_full_path() or ''
        return replace_query_param(url, self.page_field, page)


class PreviousLinkField(pagination.NextPageField):
    '''Pagination field to output URL path.'''

    def to_representation(self, value):
        if not value.has_previous():
            return None
        page = value.previous_page_number()
        request = self.context.get('request')
        url = request and request.get_full_path() or ''
        return replace_query_param(url, self.page_field, page)


class PaginationSerializer(pagination.BasePaginationSerializer):
    '''Custom pagination serializer to output only URL path (without host/port).'''

    count = serializers.ReadOnlyField(source='paginator.count')
    cur_page = serializers.ReadOnlyField(source='number')
    num_pages = serializers.ReadOnlyField(source='paginator.num_pages')
    next_link = NextLinkField(source='*')
    previous_link = PreviousLinkField(source='*')
    next = NextPageField(source='*')
    previous = PreviousPageField(source='*')
