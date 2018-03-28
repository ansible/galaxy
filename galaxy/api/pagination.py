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

from rest_framework import pagination
from rest_framework import response
from rest_framework.utils.urls import remove_query_param, replace_query_param


class PageNumberPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.get_full_path()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.get_full_path()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def get_paginated_response(self, data):
        next_link = self.get_next_link()
        next_page = (next_link.replace('/api/v1', '')
                     if next_link is not None else None)
        previous_link = self.get_previous_link()
        previous_page = (previous_link.replace('/api/v1', '')
                         if previous_link is not None else None)

        return response.Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', next_page),
            ('next_link', next_link),
            ('previous', previous_page),
            ('previous_link', previous_link),
            ('results', data),
        ]))
