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
from rest_framework import serializers as drf_serializers

from galaxy.main.models import Repository
from .serializers import BaseSerializer


__all__ = [
    'RepositorySerializer'
]


class RepositorySerializer(BaseSerializer):
    REPOSITORY_TYPE_MULTIPLE = 'multiple'
    external_url = drf_serializers.SerializerMethodField()
    repository_type = drf_serializers.SerializerMethodField()

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
            'travis_build_url',
            'travis_status_url',
            'clone_url',
            'external_url',
            'issue_tracker_url',
            'repository_type'
        )

    def get_related(self, instance):
        if not isinstance(instance, Repository):
            return {}
        related = {
            'content': reverse(
                'api:repository_content_list',
                kwargs={'pk': instance.pk}),
            'imports': reverse(
                'api:repository_import_task_list',
                kwargs={'pk': instance.pk}),
            'provider': reverse(
                'api:active_provider_detail',
                kwargs={'pk': instance.provider_namespace.provider.pk}),
        }
        if instance.provider_namespace.namespace:
            related['namespace'] = reverse(
                'api:namespace_detail',
                kwargs={'pk': instance.provider_namespace.namespace.pk})
        return related

    def get_summary_fields(self, instance):
        if not isinstance(instance, Repository):
            return {}
        owners = [{
            'id': u.id,
            'avatar_url': u.avatar_url,
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

        latest_import = {}
        import_tasks = instance.import_tasks.order_by('-id')
        if len(import_tasks):
            latest_import['id'] = import_tasks[0].id
            latest_import['state'] = import_tasks[0].state
            latest_import['started'] = import_tasks[0].started
            latest_import['finished'] = import_tasks[0].finished
            latest_import['created'] = import_tasks[0].created
            latest_import['modified'] = import_tasks[0].modified

        return {
            'owners': owners,
            'provider_namespace': provider_namespace,
            'provider': provider,
            'namespace': namespace,
            'latest_import': latest_import
        }

    def get_external_url(self, instance):
        server = ''
        if instance.provider_namespace.provider.name.lower() == 'github':
            server = 'https://github.com'
        return '{0}/{1}/{2}'.format(
            server,
            instance.provider_namespace.name,
            instance.original_name)

    def get_repository_type(self, instance):
        try:
            content_count = instance.content_count
        except AttributeError:
            content_count = instance.content_objects.count()

        if content_count > 1:
            return self.REPOSITORY_TYPE_MULTIPLE
        elif content_count > 0:
            content = instance.content_objects.first()
            return content.content_type.name
        else:
            return None
