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

from rest_framework import serializers
from rest_framework import fields

from galaxy import constants
from .collections import CollectionListSerializer


__all__ = (
    'SearchRequestSerializer',
    'CollectionSearchSerializer',
)


# TODO(cutwater): Move to fields
class SeparatedStringField(fields.Field):

    child = fields.CharField()

    def __init__(self, **kwargs):
        self.separator = kwargs.pop('separator', ' ')
        self.child = kwargs.pop('child', self.child)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        return [self.child.run_validation(item)
                for item in data.split(self.separator)]


class SearchRequestSerializer(serializers.Serializer):
    keywords = fields.CharField(default=None)
    namespaces = SeparatedStringField(
        child=fields.RegexField(regex=constants.NAME_REGEXP),
        default=None,
    )
    names = SeparatedStringField(
        child=fields.RegexField(regex=constants.NAME_REGEXP),
        default=None,
    )
    tags = SeparatedStringField(
        default=None,
    )
    contributor_type = fields.ChoiceField(
        choices=constants.NS_TYPES,
        default=None,
    )
    platforms = SeparatedStringField(default=None)
    cloud_platforms = SeparatedStringField(default=None)
    deprecated = fields.NullBooleanField(default=None)


class CollectionSearchSerializer(CollectionListSerializer):
    content_match = serializers.SerializerMethodField()

    class Meta(CollectionListSerializer.Meta):
        fields = CollectionListSerializer.Meta.fields + (
            'content_match',
        )

    def get_content_match(self, obj):
        content_match = getattr(obj, 'content_match', None)
        if not content_match:
            return None

        contents = {
            'module': [],
            'role': [],
            # Playbooks not supported yet
            # 'playbook': [],
            'plugin': []
        }

        for content in content_match:
            if content['content_type'] in contents:
                contents[content['content_type']].append(content['name'])
            else:
                contents['plugin'].append(content['name'])

        return {'total_count': len(content_match), 'contents': contents}
