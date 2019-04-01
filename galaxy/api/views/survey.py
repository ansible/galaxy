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

import logging

from galaxy.main import models
from galaxy.api import serializers
from . import base_views
from galaxy.main.celerytasks import user_notifications

from rest_framework.response import Response

logger = logging.getLogger(__name__)

__all__ = [
    'RepositorySurveyList',
    'RepositorySurveyDetail'
]

SURVEY_FIElDS = (
    'docs',
    'ease_of_use',
    'does_what_it_says',
    'works_as_is',
    'used_in_production',
)


class RepositorySurveyList(base_views.ListCreateAPIView):
    model = models.RepositorySurvey
    serializer_class = serializers.RepositorySurveySerializer

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user.id

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_community_score(serializer.validated_data['repository'])

        headers = self.get_success_headers(serializer.data)

        # Each question answered comes as a separate HTTP request, so delay
        # the email update by 2 minutes to allow for all the questions to be
        # submitted so that the score includes all of the submitted answers.
        user_notifications.new_survey.apply_async(
            (serializer.validated_data['repository'].id,),
            countdown=120
        )

        return Response(serializer.data, headers=headers)


class RepositorySurveyDetail(base_views.RetrieveUpdateDestroyAPIView):
    model = models.RepositorySurvey
    serializer_class = serializers.RepositorySurveySerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=self.get_object(),
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_community_score(serializer.validated_data['repository'])

        return Response(serializer.data)


def update_community_score(repo):
    surveys = models.RepositorySurvey.objects.filter(repository=repo)

    score = 0

    answer_count = 0
    survey_score = 0.0
    for survey in surveys:
        for k in SURVEY_FIElDS:
            data = getattr(survey, k)
            if data is not None:
                answer_count += 1
                survey_score += (data - 1) / 4

    # Average and convert to 0-5 scale
    score = (survey_score / answer_count) * 5

    repo.community_score = score
    repo.community_survey_count = len(surveys)
    repo.save()

    namespace = repo.provider_namespace.namespace.name

    fields = {
        'content_name': '{}.{}'.format(namespace, repo.name),
        'content_id': repo.id,
        'community_score': repo.community_score,
        'quality_score': repo.quality_score,
    }

    serializers.influx_insert_internal({
        'measurement': 'content_score',
        'fields': fields
    })
