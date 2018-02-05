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
    'RepositorySourceSerializer',
]


class RepositorySourceSerializer(serializers.BaseSerializer):

    fields = [
        'name',
        'description',
        'stargazers_count',
        'watchers_count',
        'forks_count',
        'open_issues_count',
        'default_branch'
    ]

    optional_fields = [
        'commit',
        'commit_message',
        'commit_url',
        'commit_created'
    ]

    def to_representation(self, instance):
        if not instance:
            return {}

        result = OrderedDict()
        provider_id = instance['provider_id']
        provider = instance['provider']
        provider_namespace = instance.get('provider_namespace')
        provider_namespace_id = instance.get('provider_namespace_id')
        namespace = instance.get('namespace')
        namespace_id = instance.get('namespace_id')

        name = instance['name'].replace('.', '-')

        result['related'] = {
            'provider': reverse('api:active_provider_detail', kwargs={'pk': provider_id}),
            'source_repository': reverse('api:repository_source_detail', kwargs={
                'provider_name': provider,
                'provider_namespace': provider_namespace,
                'repo_name': name
            })
        }

        if namespace_id:
            result['related']['namespace'] = reverse('api:namespace_detail', kwargs={'pk': namespace_id})

        # TODO add link to provider_namespace, if available in DB

        result['summary_fields'] = {
            'provider_namespace': {
                'name': provider_namespace,
                'id': provider_namespace_id
            },
            'namespace': {
                'name': namespace,
                'id': namespace_id
            }
        }

        for field in self.fields:
            result[field] = instance.get(field)

        for field in self.optional_fields:
            if field in instance:
                result[field] = instance.get(field)

        return result
