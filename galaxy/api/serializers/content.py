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

from django import urls
from rest_framework import serializers
from collections import OrderedDict

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
        fields = ('id', 'name', 'is_vendor')


class _RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Repository
        fields = (
            'id',
            'name',
            'original_name',
            'description',
            'clone_url',
            'deprecated'
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
            'role_type',
            'quality_score',
            'content_score',
            'metadata_score',
            'compatibility_score',
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
        # Support ansible-galaxy <= 2.6 by excluding unsupported messges
        supported_types = ('INFO', 'WARNING', 'ERROR', 'SUCCESS', 'FAILED')
        latest_task = models.ImportTask.objects.filter(
            repository_id=instance.repository_id).order_by('-created').first()

        task_messages = []
        if latest_task:
            messages_qs = models.ImportTaskMessage.objects.filter(
                task_id=latest_task.id,
                content_id=instance.id,
                message_type__in=supported_types,
                is_linter_rule_violation=True,
            )
            task_messages = [
                OrderedDict([
                    ('id', m.id),
                    ('message_type', m.message_type),
                    ('message_text', m.message_text),
                    ('content_id', m.content_id),
                    ('is_linter_rule_violation', m.is_linter_rule_violation),
                    ('linter_type', m.linter_type),
                    ('linter_rule_id', m.linter_rule_id),
                    ('rule_desc', m.rule_desc),
                    ('rule_severity', m.rule_severity),
                    ('score_type', m.score_type),
                ])
                for m in messages_qs
            ]

        return {
            'namespace': _NamespaceSerializer().to_representation(
                instance.repository.provider_namespace.namespace),
            'repository': _RepositorySerializer().to_representation(
                instance.repository),
            'content_type':
                _ContentTypeSerializer().to_representation(
                    instance.content_type),
            'dependencies': [str(g) for g in instance.dependencies.all()],
            'task_messages': task_messages,
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
            'dependencies': [
                {'id': d.pk, 'namespace': d.namespace.name,
                 'name': d.name}
                for d in instance.dependencies.all()],
            'versions': [
                {'id': v.id, 'version': str(v.version), 'tag': v.tag,
                 'commit_date': v.commit_date, 'commit_sha': v.commit_sha}
                for v in instance.repository.all_versions()
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
