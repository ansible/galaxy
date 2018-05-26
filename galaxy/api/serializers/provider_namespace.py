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

from django.core.urlresolvers import reverse

from galaxy.main.models import ProviderNamespace
from . import serializers


__all__ = [
    'ProviderNamespaceSerializer',
]


class ProviderNamespaceSerializer(serializers.BaseSerializer):

    class Meta:
        model = ProviderNamespace
        fields = serializers.BASE_FIELDS + (
            'id',
            'description',
            'display_name',
            'avatar_url',
            'location',
            'company',
            'email',
            'html_url',
            'followers'
        )

    def get_summary_fields(self, instance):
        result = {}
        if instance.provider:
            result['provider'] = {
                'id': instance.provider.pk,
                'name': instance.provider.name
            }
        if instance.namespace:
            result['namespace'] = {
                'id': instance.namespace.pk,
                'name': instance.namespace.name,
                'is_vendor': instance.namespace.vendor,
            }
        return result

    def get_related(self, instance):
        result = {}
        if instance.provider:
            result['provider'] = reverse(
                'api:active_provider_detail', args=(instance.provider.pk,))
        if instance.namespace:
            result['namespace'] = reverse(
                'api:namespace_detail', args=(instance.namespace.pk,))
        result['repositories'] = reverse(
            'api:provider_namespace_repositories_list',
            args=(instance.pk,))
        return result
