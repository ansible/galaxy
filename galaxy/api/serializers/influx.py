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

from . import serializers
from rest_framework import serializers as drf_serializers
from django.conf import settings

import influxdb

from galaxy.main import models

__all__ = (
    'InfluxSessionSerializer',
    'InfluxTypes',
    'PageLoadSerializer'
)


class InfluxSessionSerializer(serializers.BaseSerializer):
    class Meta:
        model = models.InfluxSessionIdentifier
        fields = (
            'session_id',
        )

    def get_url(self, obj):
        return ''

    def get_summary_fields(self, instance):
        return {}


class BaseEvent(drf_serializers.Serializer):
    measurement = drf_serializers.CharField()

    def save(self):
        client = influxdb.InfluxDBClient(
            host=settings.INFLUX_DB_HOST,
            port=settings.INFLUX_DB_PORT,
            username=settings.INFLUX_DB_USERNAME,
            password=settings.INFLUX_DB_PASSWORD
        )

        client.switch_database(settings.INFLUX_DB_DATABASE_NAME)
        client.write_points([self.data])


class BaseTags(drf_serializers.Serializer):
    session_id = drf_serializers.UUIDField()
    current_page = drf_serializers.CharField()


class BaseFields(drf_serializers.Serializer):
    count = drf_serializers.IntegerField()


# Page Load
class PageLoadTags(BaseTags):
    originating_page = drf_serializers.CharField()


class PageLoadFields(BaseFields):
    load_time = drf_serializers.IntegerField()


class PageLoadSerializer(BaseEvent):
    tags = PageLoadTags()
    fields = PageLoadFields()


InfluxTypes = {
    'page_load': PageLoadSerializer
}
