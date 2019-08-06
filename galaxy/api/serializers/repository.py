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

from django.conf import settings
from django.urls import reverse
from rest_framework import serializers as drf_serializers

from galaxy.main.models import Repository
from . import serializers


__all__ = [
    'RepositorySerializer'
]


class RepositorySerializer(serializers.BaseSerializer):
    external_url = drf_serializers.SerializerMethodField()
    readme = drf_serializers.SerializerMethodField()
    readme_html = drf_serializers.SerializerMethodField()
    download_url = drf_serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = serializers.BASE_FIELDS + (
            'id',
            'original_name',
            'description',
            'format',
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
            'download_count',
            'travis_build_url',
            'travis_status_url',
            'clone_url',
            'external_url',
            'issue_tracker_url',
            'readme',
            'readme_html',
            'download_url',
            'deprecated',
            'community_score',
            'quality_score',
            'quality_score_date',
            'community_survey_count'
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
            'versions': reverse(
                'api:repository_version_list',
                kwargs={'pk': instance.pk}),
            'provider': reverse(
                'api:active_provider_detail',
                kwargs={'pk': instance.provider_namespace.provider.pk}),
            'provider_namespace': reverse(
                'api:provider_namespace_detail',
                args=(instance.provider_namespace.pk,)),
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
        namespace_obj = instance.provider_namespace.namespace
        if namespace_obj:
            namespace = {
                'id': namespace_obj.pk,
                'name': namespace_obj.name,
                'description': namespace_obj.description,
                'is_vendor': namespace_obj.is_vendor
            }
        latest_import = {}
        import_tasks = instance.import_tasks.order_by('-id')
        if len(import_tasks):
            latest_import['id'] = import_tasks[0].id
            latest_import['state'] = import_tasks[0].state
            latest_import['started'] = import_tasks[0].started
            latest_import['finished'] = import_tasks[0].finished
            latest_import['created'] = import_tasks[0].created
            latest_import['modified'] = import_tasks[0].modified

        content_objects = [
            {
                'id': c.id,
                'name': c.name,
                'content_type': c.content_type.name,
                'description': c.description,
                'quality_score': c.quality_score,
            }
            for c in instance.content_objects.all()
        ]

        content_counts = {
            c['content_type__name']: c['count']
            for c in instance.content_counts
        }

        versions = []

        for version in instance.all_versions():
            versions.append({
                'download_url':
                    version.repository.get_download_url(version.tag),
                'version': str(version.version)
            })

        return {
            'owners': owners,
            'provider_namespace': provider_namespace,
            'provider': provider,
            'namespace': namespace,
            'latest_import': latest_import,
            'content_objects': content_objects,
            'content_counts': content_counts,
            'versions': versions
        }

    def get_external_url(self, instance):
        server = ''
        if instance.provider_namespace.provider.name.lower() == 'github':
            if 'github' in settings.SOCIALACCOUNT_PROVIDERS:
                if 'GITHUB_URL' in settings.SOCIALACCOUNT_PROVIDERS['github']:
                    server = settings \
                        .SOCIALACCOUNT_PROVIDERS['github'] \
                        .GITHUB_URL
                else:
                    server = 'https://github.com'
            else:
                server = 'https://github.com'
        return '{0}/{1}/{2}'.format(
            server,
            instance.provider_namespace.name,
            instance.original_name)

    def get_readme(self, obj):
        if obj.readme:
            return obj.readme.raw
        return None

    def get_readme_html(self, obj):
        if obj.readme:
            return obj.readme.html
        return None

    def get_download_url(self, obj):
        return obj.get_download_url()
