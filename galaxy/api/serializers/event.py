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

import copy
import logging

from galaxy import constants
from galaxy.main import models

from rest_framework import serializers as drf_serializers

from django.core.urlresolvers import reverse

from . import serializers


__all__ = (
    'EventSerializer',
)

logger = logging.getLogger(__name__)


class ValidSearchType(object):
    choices = []

    def __init__(self):
        for choice in constants.EventType.choices():
            self.choices.append(choice[0])

    def __call__(self, value):
        if value not in self.choices:
            message = '%s is not a valid choice.' % value
            raise drf_serializers.ValidationError(message)


def clean_search_data(data):
    return {
        'search_params': data.get('search_params', {}),
        'search_results': data.get('search_results', 0),
        'next_page_clicks': data.get('next_page_clicks', 0),
        'prev_page_clicks': data.get('prev_page_clicks', 0),
        'results_clicked': data.get('results_clicked', []),
        'repositories_clicked': data.get('repositories_clicked', []),
        'content_items_clicked': data.get('content_items_clicked', []),
        'last_page_size': data.get('last_page_size', 0)
    }


def append_list_to_list(source_data, target_data, label):
    if source_data.get(label):
        for item in source_data[label]:
            if item not in target_data[label]:
                target_data[label].append(item)


class EventSerializer(serializers.BaseSerializer):
    event_data = drf_serializers.JSONField()
    event_type = drf_serializers.CharField(validators=[ValidSearchType()])

    class Meta:
        model = models.SessionEvent
        fields = (
            'id',
            'url',
            'related',
            'summary_fields',
            'created',
            'modified',
            'session_id',
            'event_type',
            'event_data'
        )

    def get_url(self, instance):
        if instance is None:
            return ''
        return reverse('api:event_detail', args=(instance.pk,))

    def get_releated(self, instance):
        return{}

    def get_summary_fields(self, instance):
        return {}

    def update(self, instance, validated_data):
        event_data = clean_search_data(copy.copy(instance.event_data))
        validated_event_data = copy.copy(validated_data.get('event_data'))
        if validated_data.get('event_type') == \
                constants.EventType.SEARCH.value:
            if validated_event_data.get('next_page_clicks'):
                event_data['next_page_clicks'] += 1
            if validated_event_data.get('prev_page_clicks'):
                event_data['prev_page_clicks'] += 1
            if validated_event_data.get('last_page_size'):
                event_data['last_page_size'] = \
                    validated_event_data['last_page_size']
            for label in ('results_clicked', 'repositories_clicked',
                          'content_items_clicked'):
                append_list_to_list(
                    validated_event_data, event_data, label)
        validated_data['event_data'] = event_data
        return super(EventSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        if validated_data.get('event_type') == \
                constants.EventType.SEARCH.value:
            event_data = validated_data.get('event_data', {})
            validated_data['event_data'] = clean_search_data(event_data)
        return super(EventSerializer, self).create(validated_data)
