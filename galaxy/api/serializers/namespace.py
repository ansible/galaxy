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
from galaxy.main import models
from . import serializers


__all__ = [
    'NamespaceSerializer',
]


class NamespaceSerializer(serializers.BaseSerializer):
    class Meta:
        model = models.Namespace
        fields = serializers.BASE_FIELDS + (
            'id',
            'description',
            'avatar_url',
            'location',
            'company',
            'email',
            'html_url',
            'vendor',
        )

    def get_summary_fields(self, instance):
        owners = [{
            'id': u.id,
            'avatar_url': u.avatar_url,
            'username': u.username
        } for u in instance.owners.all()]

        provider_namespaces = [{
            'id': pn.id,
            'name': pn.name,
            'display_name': pn.display_name,
            'avatar_url': pn.avatar_url,
            'location': pn.location,
            'compay': pn.company,
            'description': pn.description,
            'email': pn.email,
            'html_url': pn.html_url,
            'provider': pn.provider.id,
            'provider_name': pn.provider.name.lower()
        } for pn in instance.provider_namespaces.all()]

        content_counts = {c['content_type__name']: c['count'] for c in instance.content_counts}

        return {
            'owners': owners,
            'provider_namespaces': provider_namespaces,
            'content_counts': content_counts
        }

    def get_related(self, instance):
        related = {
            'provider_namespaces': reverse(
                'api:namespace_provider_namespaces_list',
                args=(instance.pk,)),
            'content': reverse(
                'api:namespace_content_list',
                args=(instance.pk,)),
            'owners': reverse(
                'api:namespace_owners_list',
                args=(instance.pk,))
        }
        return related
