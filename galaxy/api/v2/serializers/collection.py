# (c) 2012-2019, Ansible by Red Hat
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

from rest_framework import exceptions as drf_exc
from rest_framework import serializers
from rest_framework.reverse import reverse

from galaxy.common.schema import CollectionFilename
from galaxy.api import fields
from galaxy.main import models
from .tasks import BaseTaskSerializer


__all__ = (
    'CollectionImportSerializer',
    'CollectionUploadSerializer',
    'CollectionSerializer',
    'VersionSummarySerializer',
    'VersionDetailSerializer',
)


class VersionSummarySerializer(serializers.ModelSerializer):
    """Collection version with short summary of data."""
    href = fields.VersionUrlField(source='*')

    class Meta:
        model = models.CollectionVersion
        fields = ('version', 'href')


class VersionDetailSerializer(serializers.ModelSerializer):
    """Collection version with detailed data."""
    id = serializers.IntegerField(source='pk')
    href = fields.VersionUrlField(source='*')
    download_url = serializers.SerializerMethodField()
    namespace = fields.NamespaceObjectField(source='collection.namespace')
    collection = serializers.SerializerMethodField()
    metadata = serializers.JSONField(binary=False)

    class Meta:
        model = models.CollectionVersion
        fields = (
            'id',
            'href',
            'download_url',
            'namespace',
            'collection',
            'version',
            'hidden',
            'metadata',
        )

    def get_download_url(self, obj):
        return reverse(
            'api:v2:version-artifact',
            kwargs={
                'namespace': obj.collection.namespace.name,
                'name': obj.collection.name,
                'version': obj.version,
            },
            request=self.context.get('request'),
        )

    def get_collection(self, obj):
        ns_name = obj.collection.namespace.name
        name = obj.collection.name
        result = {
            'id': obj.collection.pk,
            'href': reverse(
                'api:v2:collection-detail',
                kwargs={'namespace': ns_name, 'name': name},
                request=self.context.get('request'),
            ),
            'name': name,
        }
        return result


class CollectionSerializer(serializers.ModelSerializer):
    namespace = fields.NamespaceObjectField()
    href = serializers.SerializerMethodField()
    versions_url = serializers.SerializerMethodField()
    highest_version = VersionSummarySerializer()

    class Meta:
        model = models.Collection
        fields = (
            'id',
            'href',
            'name',
            'namespace',
            'versions_url',
            'highest_version',
            'deprecated',
            'created',
            'modified',
        )

    def get_href(self, obj):
        return reverse(
            'api:v2:collection-detail',
            kwargs={
                'namespace': obj.namespace.name,
                'name': obj.name,
            },
            request=self.context.get('request'),
        )

    def get_versions_url(self, obj):
        return reverse(
            'api:v2:version-list',
            kwargs={
                'namespace': obj.namespace.name,
                'name': obj.name,
            },
            request=self.context.get('request'),
        )


class _MessageSerializer(serializers.Serializer):
    level = serializers.CharField()
    message = serializers.CharField()
    time = fields.NativeTimestampField()


class CollectionImportSerializer(BaseTaskSerializer):
    messages = _MessageSerializer(many=True)
    lint_records = serializers.JSONField()

    namespace = fields.NamespaceObjectField()
    imported_version = serializers.SerializerMethodField()

    class Meta:
        model = models.CollectionImport
        fields = BaseTaskSerializer.Meta.fields + (
            'namespace', 'name', 'version',
            'messages', 'lint_records', 'imported_version',
        )

    # TODO(cutwater): Replace with custom field
    def get_imported_version(self, obj):
        if obj.imported_version is None:
            return None
        return {
            'id': obj.imported_version.pk,
            'href': reverse('api:v2:version-detail',
                            args=[obj.imported_version.pk],
                            request=self.context.get('request')),
        }


class CollectionUploadSerializer(serializers.Serializer):

    file = serializers.FileField(
        help_text="The collection file.",
        required=True,
    )

    sha256 = serializers.CharField(
        required=False,
        default=None,
    )

    def validate(self, data):
        super().validate(data)

        try:
            data['filename'] = CollectionFilename.parse(
                data['file'].name)
        except ValueError as e:
            raise drf_exc.ValidationError(str(e))

        return data
