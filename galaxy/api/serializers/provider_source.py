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
from rest_framework import serializers

__all__ = [
    'ProviderSourceSerializer',
]


class ProviderSourceSerializer(serializers.BaseSerializer):

    fields = [
        'name',
        'description',
        'display_name',
        'avatar_url',
        'location',
        'company',
        'email',
        'html_url',
        'followers',
        'provider'
    ]

    def to_representation(self, instance):
        result = OrderedDict()
        name = instance['name']
        provider_name = instance['provider_name']
        provider = instance['provider']

        result['related'] = {
            'provider': reverse('api:active_provider_detail', kwargs={'pk': provider}),
            'source_repositories': reverse('api:repository_source_list', kwargs={'provider_name': provider_name.lower(),
                                                                                 'provider_namespace': name.lower()})
        }

        result['summary_fields'] = {
            'provider': {
                'name': provider_name,
                'id': provider
            }
        }

        for field in self.fields:
            result[field] = instance[field]

        return result
