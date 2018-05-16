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

import logging

from django.core import urlresolvers as urls
from rest_framework import serializers

from galaxy.main import models


__all__ = (
    'ContentSerializer',
    'ContentDetailSerializer',
)


logger = logging.getLogger(__name__)


class BaseModelSerializer(serializers.ModelSerializer):
    BASE_FIELDS = (
        'url',
        'created',
        'modified',
        'related',
        'summary_fields',
    )

    url = serializers.SerializerMethodField()
    related = serializers.SerializerMethodField()
    summary_fields = serializers.SerializerMethodField()

    def get_url(self, instance):
        try:
            return instance.get_absolute_url()
        except AttributeError:
            return None

    def get_related(self, instance):
        return {}

    def get_summary_fields(self, instance):
        return {}


class _NamespaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Namespace
        fields = ('id', 'name')


class _RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Repository
        fields = (
            'id',
            'name',
            'original_name',
            'description',
            'clone_url'
        )


class _ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContentType
        fields = ('id', 'name', 'description')


class ContentSerializer(BaseModelSerializer):
    content_type = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.Content
        fields = BaseModelSerializer.BASE_FIELDS + (
            'id',
            'name',
            'original_name',
            'description',
            'content_type',
            'imported',
            'download_count',
            'role_type'
        )

    def get_platforms(self, instance):
        return [{'name': item.name, 'release': item.release}
                for item in instance.platforms.all()]

    def get_related(self, instance):
        return {
            'dependencies': urls.reverse(
                'api:content_dependencies_list', args=(instance.pk,)),
            'content_type': urls.reverse(
                'api:content_type_detail', args=(instance.content_type.pk,)),
            'imports': urls.reverse(
                'api:role_import_task_list', args=(instance.pk,)),
            'notifications': urls.reverse(
                'api:role_notification_list', args=(instance.pk,)),
            'repository': urls.reverse(
                'api:repository_detail', args=(instance.repository.pk,)),
            'namespace': urls.reverse(
                'api:namespace_detail', args=(instance.namespace.pk,)),
            'provider_namespace': urls.reverse(
                'api:provider_namespace_detail',
                args=(instance.repository.provider_namespace.pk,)),
            'provider': urls.reverse(
                'api:active_provider_detail',
                args=(instance.repository.provider_namespace.provider.pk,)),
        }

    def get_summary_fields(self, instance):
        return {
            'namespace': _NamespaceSerializer().to_representation(
                instance.repository.provider_namespace.namespace),
            'repository': _RepositorySerializer().to_representation(
                instance.repository),
            'content_type':
                _ContentTypeSerializer().to_representation(
                    instance.content_type),
            'dependencies': [str(g) for g in instance.dependencies.all()]
        }


class ContentDetailSerializer(ContentSerializer):

    readme = serializers.SerializerMethodField()
    readme_html = serializers.SerializerMethodField()

    class Meta(ContentSerializer.Meta):
        fields = ContentSerializer.Meta.fields + (
            'container_yml',
            'metadata',
            'readme',
            'readme_html',
            'min_ansible_container_version',
            'min_ansible_version'
        )

    def get_summary_fields(self, instance):
        result = super(
            ContentDetailSerializer, self).get_summary_fields(instance)
        result.update({
            'platforms': self.get_platforms(instance),
            'cloud_platforms': [
                p.name for p in instance.cloud_platforms.all()],
            'tags': [t.name for t in instance.tags.all()],
            'dependencies': [dict(
                id=g.pk,
                namespace=g.namespace.name,
                name=g.name) for g in instance.dependencies.all()],
            'versions': [
                dict(id=g.id, name=g.name, release_date=g.release_date)
                for g in instance.repository.versions.all()
            ],
        })
        return result

    def get_readme(self, obj):
        if obj.readme:
            return obj.readme.raw
        return None

    def get_readme_html(self, obj):
        if obj.readme:
            return obj.readme.html
        return None
