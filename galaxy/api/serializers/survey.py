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
)


class RepositorySurveySerializer(serializers.BaseSerializer):
    class Meta:
        model = models.RepositorySurvey
        fields = (
            'id',
            'url',
            'repository',
            'user',
            'docs',
            'ease_of_use',
            'does_what_it_says',
            'works_as_is',
            'used_in_production'
        )

    def validate(self, data):
        repo = data.get('repository')
        user = data.get('user')

        is_owner = user in repo.provider_namespace.namespace.owners.all()

        if is_owner:
            message = 'Users are not permitted to rate their own content.'
            raise drf_serializers.ValidationError(message)

        return data

    def get_url(self, obj):
        if obj is None:
            return ''
        return reverse('api:community_survey_detail', args=(obj.pk,))

    def get_summary_fields(self, instance):
        return {
            'repository': {
                'name': instance.repository.name,
                'community_score': instance.repository.community_score
            }
        }
