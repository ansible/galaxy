# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (c) 2013 AnsibleWorks, Inc.
# All Rights Reserved.

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
        return replace_query_param(url, self.page_field, page)


class PreviousPageField(pagination.NextPageField):
    '''Pagination field to output URL path.'''

    def to_representation(self, value):
        if not value.has_previous():
            return None
        page = value.previous_page_number()
        request = self.context.get('request')
        url = request and request.get_full_path() or ''
        return replace_query_param(url, self.page_field, page)


class PaginationSerializer(pagination.BasePaginationSerializer):
    '''
    Custom pagination serializer to output only URL path (without host/port).
    '''

    count = serializers.ReadOnlyField(source='paginator.count')
    cur_page = serializers.ReadOnlyField(source='number')
    num_pages = serializers.ReadOnlyField(source='paginator.num_pages')
    next = NextPageField(source='*')
    previous = PreviousPageField(source='*')

