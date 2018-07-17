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
from rest_framework.serializers import BaseSerializer


__all__ = ['RepositorySourceSerializer']


class RepositorySourceSerializer(BaseSerializer):

    fields = [
        'name',
        'description',
        'stargazers_count',
        'watchers_count',
        'forks_count',
        'open_issues_count',
        'default_branch',
    ]

    optional_fields = [
        'commit',
        'commit_message',
        'commit_url',
        'commit_created',
    ]

    def to_representation(self, instance):
        if not instance:
            return {}

        result = OrderedDict()
        provider_id = instance['provider']['id']
        provider_name = instance['provider']['name']
        source_namespace = instance['source_namespace']
        name = instance['name'].replace('.', '-')

        result['related'] = {
            'provider': reverse(
                'api:active_provider_detail', kwargs={'pk': provider_id}
            ),
            'source_repository': reverse(
                'api:repository_source_detail',
                kwargs={
                    'provider_name': provider_name,
                    'provider_namespace': source_namespace,
                    'repo_name': name,
                },
            ),
        }

        if instance.get('namespace_url'):
            result['related']['namespace'] = instance['namespace_url']
        if instance.get('provider_namespace_url'):
            result['related']['provider_namespace'] = instance[
                'provider_namespace_url'
            ]
        if instance.get('repository_url'):
            result['related']['repository'] = instance['repository_url']

        result['summary_fields'] = {'provider': instance['provider']}

        if instance.get('provider_namespace'):
            result['summary_fields']['provider_namespace'] = instance[
                'provider_namespace'
            ]
        if instance.get('namespace'):
            result['summary_fields']['namespace'] = instance['namespace']
        if instance.get('repository'):
            result['summary_fields']['repository'] = instance['repository']

        for field in self.fields:
            result[field] = instance.get(field)

        for field in self.optional_fields:
            if field in instance:
                result[field] = instance.get(field)

        return result
