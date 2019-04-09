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


class VersionSerializer(serializers.ModelSerializer):
    metadata = serializers.JSONField(binary=False)
    contents = serializers.JSONField(binary=False)

    class Meta:
        model = models.CollectionVersion
        fields = (
            'version',
            'metadata',
            'quality_score',
            'readme_html',
            'contents',
        )


class CollectionListSerializer(serializers.ModelSerializer):
    latest_version = VersionSerializer()

    class Meta:
        model = models.Collection
        fields = (
            'namespace',
            'name',
            'deprecated',
            'download_count',
            'community_score',
            'community_survey_count',
            'latest_version',
        )
