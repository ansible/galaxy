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

from pulpcore.app import models as pulp_models


__all__ = (
    'BaseTaskSerializer',
)


class BaseTaskSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='_id')
    job_id = serializers.UUIDField()
    state = serializers.CharField()
    started_at = serializers.DateTimeField()
    finished_at = serializers.DateTimeField()
    error = serializers.JSONField()

    class Meta:
        model = pulp_models.Task
        fields = ('id', 'job_id', 'started_at', 'finished_at',
                  'state', 'error')
        read_only_fields = fields
