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

from galaxy.main.models import Repository
from .serializers import BaseSerializer


__all__ = [
    'RepositorySerializer',
]


class RepositorySerializer(BaseSerializer):
    class Meta:
        model = Repository
        fields = (
            'id',
            'name',
            'original_name',
            'description',
            'import_branch',
            'is_enabled',
            'commit',
            'commit_message',
            'commit_url',
            'commit_created',
            'stargazers_count',
            'watchers_count',
            'forks_count',
            'open_issues_count',
            # TODO(cutwater): github_user and github_repo are obsolete and
            # will be removed
            'github_user',
            'github_repo',
        )

    def get_related(self, instance):
        if not isinstance(instance, Repository):
            return {}
        related = {
            'provider': reverse('api:active_provider_detail', kwargs={'pk': instance.provider_namespace.provider.pk}),
            'provider_namespace': None
        }
        if instance.provider_namespace.namespace:
            related['namespace'] = reverse('api:namespace_detail',
                                           kwargs={'pk': instance.provider_namespace.namespace.pk})
        return related

    def get_summary_fields(self, instance):
        if not isinstance(instance, Repository):
            return {}
        owners = [{
            'id': u.id,
            'github_user': u.github_user,
            'github_avatar': u.github_avatar,
            'username': u.username
        } for u in instance.owners.all()]
        provider_namespace = {
            'name': instance.provider_namespace.name,
            'id': instance.provider_namespace.pk
        }
        provider = {
            'name': instance.provider_namespace.provider.name,
            'id': instance.provider_namespace.provider.id,
        }
        namespace = {}
        if instance.provider_namespace.namespace:
            namespace['name'] = instance.provider_namespace.namespace.name
            namespace['id'] = instance.provider_namespace.namespace.pk
        return {
            'owners': owners,
            'provider_namespace': provider_namespace,
            'provider': provider,
            'namespace': namespace
        }
