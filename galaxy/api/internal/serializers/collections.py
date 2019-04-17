
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
from galaxy.main import models


COLLECTION_LIST_FIELDS = (
    'id',
    'created',
    'modified',
    'namespace',
    'name',
    'deprecated',
    'download_count',
    'community_score',
    'latest_version',
    'community_survey_count'
)

VERSION_LIST_FIELDS = (
    'pk',
    'version',
    'quality_score',
    'created',
    'modified',
)


class VersionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CollectionVersion
        fields = VERSION_LIST_FIELDS


class VersionDetailSerializer(serializers.ModelSerializer):
    metadata = serializers.JSONField(binary=False)
    contents = serializers.JSONField(binary=False)

    class Meta:
        model = models.CollectionVersion
        fields = VERSION_LIST_FIELDS + (
            'metadata',
            'contents',
            'readme_html'
        )


class CollectionListSerializer(serializers.ModelSerializer):
    latest_version = VersionDetailSerializer()

    class Meta:
        model = models.Collection
        fields = COLLECTION_LIST_FIELDS


class CollectionDetailSerializer(serializers.ModelSerializer):
    all_versions = serializers.SerializerMethodField()
    latest_version = VersionDetailSerializer()

    class Meta:
        model = models.Collection
        fields = COLLECTION_LIST_FIELDS + ('all_versions', )
        depth = 1

    def get_all_versions(self, obj):
        versions = models.CollectionVersion.objects.filter(
            collection=obj,
            hidden=False
        )
        return VersionListSerializer(versions, many=True).data
