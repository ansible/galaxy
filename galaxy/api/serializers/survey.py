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

from rest_framework import serializers as drf_serializers
from django.urls import reverse

from . import serializers
from galaxy.main import models


__all__ = (
    'RepositorySurveySerializer',
    'CollectionSurveySerializer'
)


SHARED_FIELDS = (
            'id',
            'url',
            'user',
            'docs',
            'ease_of_use',
            'does_what_it_says',
            'works_as_is',
            'used_in_production',
            'content_id'
        )


class CollectionSurveySerializer(serializers.BaseSerializer):
    content_id = drf_serializers.SerializerMethodField()

    class Meta:
        model = models.CollectionSurvey
        fields = SHARED_FIELDS + ('collection', )

    def validate(self, data):
        collection = data.get('collection')
        user = data.get('user')

        validate_not_owner(collection.namespace.is_owner(user))

        return data

    def get_url(self, obj):
        if obj is None:
            return ''
        return reverse('api:collection_survey_detail', args=(obj.pk,))

    def get_summary_fields(self, instance):
        return {
            'content': {
                'name': instance.collection.name,
                'community_score': instance.collection.community_score,
                'type': 'collection'
            }
        }

    def get_content_id(self, obj):
        return obj.collection.id


class RepositorySurveySerializer(serializers.BaseSerializer):
    content_id = drf_serializers.SerializerMethodField()

    class Meta:
        model = models.RepositorySurvey
        fields = SHARED_FIELDS + ('repository', )

    def validate(self, data):
        repo = data.get('repository')
        user = data.get('user')

        validate_not_owner(repo.provider_namespace.namespace.is_owner(user))

        return data

    def get_url(self, obj):
        if obj is None:
            return ''
        return reverse('api:repository_survey_detail', args=(obj.pk,))

    def get_summary_fields(self, instance):
        return {
            'content': {
                'name': instance.repository.name,
                'community_score': instance.repository.community_score,
                'type': 'repository'
            }
        }

    def get_content_id(self, obj):
        return obj.repository.id


def validate_not_owner(is_owner):
    if is_owner:
        message = 'Users are not permitted to rate their own content.'
        raise drf_serializers.ValidationError(message)
