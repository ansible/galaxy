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
    'CommunitySurveyList',
    'CommunitySurveyDetail'
]

SURVEY_FIElDS = (
    'docs',
    'ease_of_use',
    'does_what_it_says',
    'works_as_is',
    'used_in_production',
)


class CommunitySurveyList(base_views.ListCreateAPIView):
    model = models.CommunitySurvey
    serializer_class = serializers.CommunitySurveySerializer

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user.id

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_community_score(serializer.validated_data['repository'])

        headers = self.get_success_headers(serializer.data)

        # Each question answered comes as a separate POST request, so delay
        # the email update by 2 minutes to allow for all the questions to be
        # submitted so that the score includes all of the submitted answers.
        user_notifications.new_survey.apply_async(
            (serializer.validated_data['repository'].id,),
            countdown=120
        )

        return Response(serializer.data, headers=headers)


class CommunitySurveyDetail(base_views.RetrieveUpdateDestroyAPIView):
    model = models.CommunitySurvey
    serializer_class = serializers.CommunitySurveySerializer

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
    surveys = models.CommunitySurvey.objects.filter(repository=repo)

    score = 0

    for survey in surveys:
        survey_score = 0.0
        answer_count = 0
        for k in SURVEY_FIElDS:
            data = getattr(survey, k)
            if data is not None:
                answer_count += 1
                # Normalize on a scale of 0 to 1
                survey_score += (data - 1) / 4.0

        if answer_count != 0:
            score += (survey_score / answer_count)

    # Average and convert to 0-5 scale
    score = (score / len(surveys)) * 5

    repo.community_score = score
    repo.save()
