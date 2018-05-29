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

from rest_framework import serializers as drf_serializers
from django.core.urlresolvers import reverse

from galaxy.main.models import Content
from .serializers import BaseSerializer, BASE_FIELDS


__all__ = [
    'RoleListSerializer',
    'RoleDetailSerializer',
    'RoleSearchSerializer',
]


class BaseRoleSerializer(BaseSerializer):
    REPOSITORY_MOVED_FIELDS = (
        'github_user',
        'github_repo',
        ('github_branch', 'import_branch'),
        'stargazers_count',
        'forks_count',
        'open_issues_count',
        'commit',
        'commit_message',
        'commit_url',
        'issue_tracker_url'
    )

    def _get_repository_moved_fields(self, instance):
        result = {}
        repository = instance.repository
        for name in self.REPOSITORY_MOVED_FIELDS:
            if isinstance(name, tuple):
                old_name, new_name = name
            else:
                old_name = new_name = name
            result[old_name] = getattr(repository, new_name)
        return result

    def to_representation(self, instance):
        result = (
            super(BaseRoleSerializer, self)
            .to_representation(instance))
        result.update(self._get_repository_moved_fields(instance))
        return result


class RoleListSerializer(BaseRoleSerializer):

    class Meta:
        model = Content
        fields = BASE_FIELDS + (
            'role_type', 'is_valid',
            'min_ansible_version',
            'license', 'company', 'description',
            'travis_status_url', 'download_count', 'imported'
        )

    def to_native(self, obj):
        ret = super(RoleListSerializer, self).to_native(obj)
        return ret

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleListSerializer, self).get_related(obj)
        res.update(dict(
            content_type=reverse(
                'api:content_type_detail', args=(obj.content_type.pk,)),
            dependencies=reverse(
                'api:role_dependencies_list', args=(obj.pk,)),
            imports=reverse(
                'api:role_import_task_list', args=(obj.pk,)),
        ))
        return res

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Content):
            return reverse('api:role_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RoleListSerializer, self).get_summary_fields(obj)
        d['content_type'] = dict(
            id=obj.content_type.id,
            name=obj.content_type.name,
            description=obj.content_type.description)
        d['dependencies'] = [str(g) for g in obj.dependencies.all()]
        d['namespace'] = dict(
            id=obj.repository.provider_namespace.namespace.pk,
            name=obj.repository.provider_namespace.namespace.name,
            avatar_url=obj.repository.provider_namespace.namespace.avatar_url,
            location=obj.repository.provider_namespace.namespace.location,
            company=obj.repository.provider_namespace.namespace.company,
            email=obj.repository.provider_namespace.namespace.email,
            html_url=obj.repository.provider_namespace.namespace.html_url)
        d['platforms'] = [
            dict(name=g.name, release=g.release) for g in obj.platforms.all()]
        d['provider_namespace'] = dict(
            id=obj.repository.provider_namespace.pk,
            name=obj.repository.provider_namespace.name)
        d['repository'] = dict(
            id=obj.repository.pk,
            name=obj.repository.name,
            original_name=obj.repository.original_name,
            stargazers_count=obj.repository.stargazers_count,
            watchers_count=obj.repository.watchers_count,
            forks_count=obj.repository.forks_count,
            open_issues_count=obj.repository.open_issues_count,
            travis_status_url=obj.repository.travis_status_url,
            travis_build_url=obj.repository.travis_build_url,
            format=obj.repository.format)
        d['tags'] = [g.name for g in obj.tags.all()]
        d['versions'] = [
            dict(id=g.id, name=g.name, release_date=g.release_date)
            for g in obj.repository.versions.all()]
        d['videos'] = [dict(url=v.url, description=v.description)
                       for v in obj.videos.all()]
        return d

    def get_issue_tracker_url(self, obj):
        if not obj:
            return None
        return obj.repository.issue_tracker_url


class RoleDetailSerializer(BaseRoleSerializer):

    readme = drf_serializers.SerializerMethodField()
    readme_html = drf_serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = BASE_FIELDS + (
            'role_type', 'namespace', 'is_valid',
            'min_ansible_version', 'license', 'company',
            'description', 'readme', 'readme_html', 'travis_status_url',
            'created', 'modified', 'download_count', 'imported')

    def to_native(self, obj):
        ret = super(RoleDetailSerializer, self).to_native(obj)
        return ret

    def get_related(self, obj):
        if obj is None:
            return {}
        res = super(RoleDetailSerializer, self).get_related(obj)
        res.update(dict(
            dependencies=reverse('api:role_dependencies_list', args=(obj.pk,)),
            imports=reverse('api:role_import_task_list', args=(obj.pk,)),
        ))
        return res

    def get_url(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, Content):
            return reverse('api:role_detail', args=(obj.pk,))
        else:
            return obj.get_absolute_url()

    def get_summary_fields(self, obj):
        if obj is None:
            return {}
        d = super(RoleDetailSerializer, self).get_summary_fields(obj)
        d['dependencies'] = [dict(id=g.id, name=str(g))
                             for g in obj.dependencies.all()]
        d['namespace'] = dict(
            id=obj.repository.provider_namespace.namespace.pk,
            name=obj.repository.provider_namespace.namespace.name)
        d['platforms'] = [dict(name=g.name, release=g.release)
                          for g in obj.platforms.all()]
        d['provider_namespace'] = dict(
            id=obj.repository.provider_namespace.pk,
            name=obj.repository.provider_namespace.name)
        d['repository'] = dict(id=obj.repository.pk, name=obj.repository.name)
        d['tags'] = [g.name for g in obj.tags.all()]
        d['versions'] = [dict(id=g.id, name=g.name,
                              release_date=g.release_date)
                         for g in obj.repository.versions.all()]
        d['videos'] = [dict(url=v.url, description=v.description)
                       for v in obj.videos.all()]
        return d

    def get_readme(self, obj):
        if obj.readme:
            return obj.readme.raw
        return None

    def get_readme_html(self, obj):
        if obj.readme:
            return obj.readme.html
        return None


class RoleSearchSerializer(RoleListSerializer):

    relevance = drf_serializers.FloatField()
    search_rank = drf_serializers.FloatField()
    download_rank = drf_serializers.FloatField()

    class Meta(RoleListSerializer.Meta):
        fields = RoleListSerializer.Meta.fields + (
            'relevance',
            'search_rank',
            'download_rank',
        )
