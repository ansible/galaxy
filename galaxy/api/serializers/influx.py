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


influx_insert_buffer = []
####################################################
# Influx "Schema"
####################################################
# Influx doesn't have set schema's like most relational databases have, so it's
# up to the programmer to enforce some level of strcture to the data at the
# application level. Galaxy is currently using Django Rest Framework
# to verify that the shape of the data is correct before we insert it into
# influx. This means that the following serializers are roughly equivalent to
# models, and should be changed as little as possible to ensure data
# consistency.


# Influx data is organized into 'measurements' which are roughly equivalent to
# database tables. Each measurement contains at least one field and zero to
# many tags. Fields and tags are similar to columns with a few caveats.


class BaseMeasurement(drf_serializers.Serializer):
    measurement = drf_serializers.CharField()

    def save(self):
        if not settings.GALAXY_METRICS_ENABLED:
            return

        global influx_insert_buffer
        if len(influx_insert_buffer) < settings.INFLUX_INSERT_BUFFER_COUNT:
            influx_insert_buffer.append(self.data)
        else:
            client = influxdb.InfluxDBClient(
                host=settings.INFLUX_DB_HOST,
                port=settings.INFLUX_DB_PORT,
                username=settings.INFLUX_DB_USERNAME,
                password=settings.INFLUX_DB_PASSWORD
            )

            client.switch_database(settings.INFLUX_DB_UI_EVENTS_DB_NAME)

            try:
                client.write_points(influx_insert_buffer)
            except influxdb.client.InfluxDBClientError:
                client.create_database(settings.INFLUX_DB_UI_EVENTS_DB_NAME)
                client.switch_database(settings.INFLUX_DB_UI_EVENTS_DB_NAME)
                client.write_points(influx_insert_buffer)

            influx_insert_buffer = []
            client.close()


# Tags are indexed and only support string types. They should be used grouping
# data that will be queried frequently, but should not be used for variables
# that can have a large number of values (search keywords, repository names,
# sessions etc). Data can be grouped by tags, but the number of distinct tags
# cannot be easily counted.
class BaseTags(drf_serializers.Serializer):
    current_component = drf_serializers.CharField(allow_blank=True)


# Fields are not indexed, but can be numeric or string types. Database
# functions such as DISTINCT, COUNT, SUM, AVERAGE etc can be used on fields.
class BaseFields(drf_serializers.Serializer):
    session_id = drf_serializers.UUIDField()
    current_page = drf_serializers.CharField()


# The influx library expects data to be shaped like so:
#
# {
#     "measurement": "measurment_name",
#     "tags": {
#         "tag1": "value",
#     },
#     "fields": {
#         "field1": 1
#     }
# }

# Page Load
class PageLoadMeasurementSerializer(BaseMeasurement):
    class Tags(BaseTags):
        from_component = drf_serializers.CharField(allow_blank=True)

    class Fields(BaseFields):
        load_time = drf_serializers.FloatField()
        from_page = drf_serializers.CharField()

    tags = Tags()
    fields = Fields()


# Search
class SearchQueryMeasurementSerializer(BaseMeasurement):
    class Tags(BaseTags):
        cloud_platforms = drf_serializers.CharField(
            required=False, allow_blank=True
        )
        vendor = drf_serializers.BooleanField(required=False)
        deprecated = drf_serializers.BooleanField(required=False)
        content_type = drf_serializers.CharField(
            required=False,
            allow_blank=True
        )
        platforms = drf_serializers.CharField(required=False, allow_blank=True)
        tags = drf_serializers.CharField(required=False, allow_blank=True)
        order_by = drf_serializers.CharField(required=False, allow_blank=True)

    class Fields(BaseFields):
        keywords = drf_serializers.CharField(required=False, allow_blank=True)
        namespaces = drf_serializers.CharField(
            required=False,
            allow_blank=True
        )
        number_of_results = drf_serializers.IntegerField()

    tags = Tags()
    fields = Fields()


class SearchLinkMeasurementSerializer(BaseMeasurement):
    class Tags(BaseTags):
        cloud_platforms = drf_serializers.CharField(
            required=False, allow_blank=True
        )
        vendor = drf_serializers.BooleanField(required=False)
        deprecated = drf_serializers.BooleanField(required=False)
        content_type = drf_serializers.CharField(
            required=False,
            allow_blank=True
        )
        platforms = drf_serializers.CharField(required=False, allow_blank=True)
        tags = drf_serializers.CharField(required=False, allow_blank=True)
        order_by = drf_serializers.CharField(required=False, allow_blank=True)

    class Fields(BaseFields):
        content_clicked = drf_serializers.CharField()
        content_clicked_id = drf_serializers.IntegerField()
        position_in_results = drf_serializers.IntegerField()
        download_rank = drf_serializers.FloatField()
        search_rank = drf_serializers.FloatField()
        relevance = drf_serializers.FloatField()
        keywords = drf_serializers.CharField(required=False, allow_blank=True)

    tags = Tags()
    fields = Fields()


# UI Interactions
class ButtonClickMeasurementSerializer(BaseMeasurement):
    class Fields(BaseFields):
        name = drf_serializers.CharField()

    tags = BaseTags()
    fields = Fields()


class LinkClickMeasurementSerializer(BaseMeasurement):
    class Fields(BaseFields):
        name = drf_serializers.CharField()
        href = drf_serializers.CharField(allow_blank=True)

    tags = BaseTags()
    fields = Fields()


InfluxTypes = {
    'page_load': PageLoadMeasurementSerializer,
    'search_query': SearchQueryMeasurementSerializer,
    'search_click': SearchLinkMeasurementSerializer,
    'button_click': ButtonClickMeasurementSerializer,
    'link_click': LinkClickMeasurementSerializer
}
