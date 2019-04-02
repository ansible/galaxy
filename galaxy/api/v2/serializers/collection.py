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
)


class _MessageSerializer(serializers.Serializer):
    level = serializers.CharField()
    message = serializers.CharField()
    time = fields.NativeTimestampField()


class CollectionImportSerializer(BaseTaskSerializer):
    messages = _MessageSerializer(many=True)
    lint_records = serializers.JSONField()

    namespace = serializers.SerializerMethodField()
    imported_version = serializers.SerializerMethodField()

    class Meta:
        model = models.CollectionImport
        fields = BaseTaskSerializer.Meta.fields + (
            'namespace', 'name', 'version',
            'messages', 'lint_records', 'imported_version',
        )

    def get_namespace(self, obj):
        return {
            'id': obj.namespace.pk,
            'href': '#'
        }

    def get_imported_version(self, obj):
        if obj.imported_version is None:
            return None
        return {
            'id': obj.imported_version.pk,
            'href': reverse('api:v2:collection-version-detail',
                            args=[obj.imported_version.pk]),
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
