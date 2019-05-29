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

from galaxy.common.survey import calculate_survey_score

logger = logging.getLogger(__name__)

__all__ = [
    'RepositorySurveyList',
    'RepositorySurveyDetail',
    'CollectionSurveyList',
    'CollectionSurveyDetail'
]


class CollectionSurveyList(base_views.ListCreateAPIView):
    model = models.CollectionSurvey
    serializer_class = serializers.CollectionSurveySerializer

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        request.data['collection'] = request.data['content_id']

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_collection_score(serializer.validated_data['collection'])

        headers = self.get_success_headers(serializer.data)

        # Each question answered comes as a separate HTTP request, so delay
        # the email update by 2 minutes to allow for all the questions to be
        # submitted so that the score includes all of the submitted answers.
        user_notifications.collection_new_survey.apply_async(
            (serializer.validated_data['collection'].id,),
            countdown=120
        )

        return Response(serializer.data, headers=headers)


class CollectionSurveyDetail(base_views.RetrieveUpdateDestroyAPIView):
    model = models.CollectionSurvey
    serializer_class = serializers.CollectionSurveySerializer

    def update(self, request, *args, **kwargs):
        request.data['collection'] = request.data['content_id']
        serializer = self.get_serializer(
            instance=self.get_object(),
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_collection_score(serializer.validated_data['collection'])

        return Response(serializer.data)


class RepositorySurveyList(base_views.ListCreateAPIView):
    model = models.RepositorySurvey
    serializer_class = serializers.RepositorySurveySerializer

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        request.data['repository'] = request.data['content_id']

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_repo_score(serializer.validated_data['repository'])

        headers = self.get_success_headers(serializer.data)

        # Each question answered comes as a separate HTTP request, so delay
        # the email update by 2 minutes to allow for all the questions to be
        # submitted so that the score includes all of the submitted answers.
        user_notifications.repo_new_survey.apply_async(
            (serializer.validated_data['repository'].id,),
            countdown=120
        )

        return Response(serializer.data, headers=headers)


class RepositorySurveyDetail(base_views.RetrieveUpdateDestroyAPIView):
    model = models.RepositorySurvey
    serializer_class = serializers.RepositorySurveySerializer

    def update(self, request, *args, **kwargs):
        request.data['repository'] = request.data['content_id']
        serializer = self.get_serializer(
            instance=self.get_object(),
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_repo_score(serializer.validated_data['repository'])

        return Response(serializer.data)


def update_repo_score(repo):
    surveys = models.RepositorySurvey.objects.filter(repository=repo)

    score = calculate_survey_score(surveys)

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


def update_collection_score(collection):
    surveys = models.CollectionSurvey.objects.filter(collection=collection)

    score = calculate_survey_score(surveys)

    collection.community_score = score
    collection.community_survey_count = len(surveys)
    collection.save()

    # TODO(newswangerd): make logger work on collections
    # namespace = repo.provider_namespace.namespace.name
    #
    # fields = {
    #     'content_name': '{}.{}'.format(namespace, repo.name),
    #     'content_id': repo.id,
    #     'community_score': repo.community_score,
    #     'quality_score': repo.quality_score,
    # }
    #
    # serializers.influx_insert_internal({
    #     'measurement': 'content_score',
    #     'fields': fields
    # })
