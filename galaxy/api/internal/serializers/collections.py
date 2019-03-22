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

__all__ = [
    'CollectionListSerializer',
]


class VersionSerializer(serializers.ModelSerializer):
    metadata = serializers.JSONField(binary=False)

    class Meta:
        model = models.CollectionVersion
        fields = (
            'version',
            'metadata',
            'contents'
        )


class CollectionListSerializer(serializers.ModelSerializer):
    community_survey_count = serializers.SerializerMethodField()
    quality_score = serializers.SerializerMethodField()
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = models.Collection
        fields = (
            'namespace',
            'name',
            'deprecated',
            'download_count',
            'community_score',
            'quality_score',
            'community_survey_count',
            'latest_version',
        )

    def get_community_survey_count(self, obj):
        return 0

    def get_quality_score(self, obj):
        latest_version = models.CollectionVersion.objects.filter(
            collection=obj
        ).latest('pk')

        return latest_version.quality_score

    def get_latest_version(self, obj):
        latest_version = models.CollectionVersion.objects.filter(
            collection=obj
        ).latest('pk')

        return VersionSerializer(latest_version).data
