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
import re

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

from rest_framework.exceptions import (ValidationError,
                                       APIException,
                                       PermissionDenied)
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status

from galaxy.accounts.models import CustomUser as User
from galaxy.api.githubapi import GithubAPI
from galaxy.api.filters import FieldLookupBackend, OrderByBackend
from galaxy.api import serializers
from galaxy.api import tasks
from galaxy.api.views import base_views as views
from galaxy.main import models


__all__ = [
    'RepositoryList',
    'RepositoryDetail',
    'RepositoryImportTaskList',
    'RepositoryContentList',
    'RepositoryVersionList',
]

logger = logging.getLogger(__name__)


def get_repo(provider_namespace, user, repo_name):
    repo = {}
    if provider_namespace.provider.name.lower() == 'github':
        # Check that the user has access to the requested repo
        repos = GithubAPI(user=user).get_namespace_repositories(
            provider_namespace.name, name=repo_name)
        if repos:
            repo = repos[0]
    return repo


def check_name(name):
    if not name:
        raise ValidationError(detail={'name': 'Name is required'})

    if not re.match('^[\w-]+$', name):
        # Allow only names containing word chars and '-'
        raise ValidationError(detail={
            'name': 'Name contains invalid characters. '
                    'Must match [A-Za-z0-9-_].'
        })


GITHUB_REPO_FIELDS = [
    'commit',
    'commit_message',
    'commit_url',
    'commit_created',
    'stargazers_count',
    'watchers_count',
    'forks_count',
    'open_issues_count'
]


class RepositoryList(views.ListCreateAPIView):
    model = models.Repository
    serializer_class = serializers.RepositorySerializer
    filter_backends = (FieldLookupBackend, SearchFilter, OrderByBackend)

    def get_queryset(self):
        qs = super(RepositoryList, self).get_queryset()
        return qs.annotate(content_count=Count('content_objects'))

    def post(self, request, *args, **kwargs):
        data = request.data
        owners = data.pop('owners', [])
        if not data.get('provider_namespace'):
            raise ValidationError(
                detail={'provider_namespace': 'Value required'})

        check_name(data.get('name'))

        try:
            provider_namespace = models.ProviderNamespace.objects.get(
                pk=data['provider_namespace'])
        except ObjectDoesNotExist:
            raise ValidationError(
                detail={'provider_namespace': 'Invalid value'})

        original_name = data.get('original_name', data['name'])

        data['name'] = data['name'].lower()

        if not request.user.is_staff:
            repo = get_repo(provider_namespace, request.user, original_name)
            if not repo:
                raise PermissionDenied(
                    "User does not have access to {0}/{1} in "
                    "GitHub".format(provider_namespace.name, original_name))
            for field in GITHUB_REPO_FIELDS:
                data[field] = repo[field]

        if not data.get('original_name'):
            data['original_name'] = original_name

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        data['provider_namespace'] = provider_namespace
        try:
            repository = models.Repository.objects.create(**data)
        except Exception as exc:
            raise APIException('Error creating repository: {0}'
                               .format(exc.message))

        for owner_pk in owners:
            try:
                owner = User.objects.get(pk=owner_pk)
            except ObjectDoesNotExist:
                pass
            else:
                owner.repositories.add(repository)

        import_task = tasks.create_import_task(repository, request.user)

        serializer = self.get_serializer(repository)
        data = serializer.data
        data['summary_fields']['latest_import'] = \
            serializers.ImportTaskSerializer(import_task).data
        headers = self.get_success_headers(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class RepositoryDetail(views.RetrieveUpdateDestroyAPIView):
    model = models.Repository
    serializer_class = serializers.RepositorySerializer
    filter_backends = (FieldLookupBackend, SearchFilter, OrderByBackend)

    def update(self, request, *args, **kwargs):
        data = request.data
        owners = data.pop('owners', [])
        instance = self.get_object()

        if data.get('provider_namespace'):
            try:
                provider_namespace = models.ProviderNamespace.objects.get(
                    pk=data['provider_namespace'])
            except ObjectDoesNotExist:
                raise ValidationError(
                    detail={'provider_namespace': 'Invalid value'})
        else:
            provider_namespace = instance.provider_namespace

        check_name(data.get('name'))

        original_name = data.get('original_name', instance.original_name)

        if not request.user.is_staff:
            repo = get_repo(provider_namespace, request.user, original_name)
            if not repo:
                raise PermissionDenied(
                    "User does not have access to {0}/{1} in "
                    "GitHub".format(provider_namespace.name, original_name))
            for field in GITHUB_REPO_FIELDS:
                data[field] = repo[field]

        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)

        try:
            # FIXME(cutwater): This code should be refactored.
            repository = models.Repository.objects.get(pk=instance.pk)
            for k in data:
                setattr(repository, k, data[k])
            repository.save()
        except Exception as exc:
            raise APIException('Error updating repository: {0}'
                               .format(exc.message))

        for owner_pk in owners:
            try:
                owner = User.objects.get(pk=owner_pk)
            except ObjectDoesNotExist:
                pass
            else:
                owner.repositories.add(instance)

        if not request.user.repositories.filter(pk=instance.pk):
            request.user.repositories.add(instance)

        import_task = tasks.create_import_task(repository, request.user)

        serializer = self.get_serializer(instance=instance)
        data = serializer.data
        data['summary_fields']['latest_import'] = \
            serializers.ImportTaskSerializer(import_task).data
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_staff:
            try:
                instance.provider_namespace.namespace.owners.get(pk=request.user.pk)
            except ObjectDoesNotExist:
                raise PermissionDenied()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RepositoryImportTaskList(views.SubListAPIView):
    view_name = "Repository Imports"
    model = models.ImportTask
    serializer_class = serializers.ImportTaskSerializer
    parent_model = models.Repository
    relationship = "import_tasks"


class RepositoryContentList(views.SubListAPIView):
    view_name = "Repository Content"
    model = models.Content
    serializer_class = serializers.ContentSerializer
    parent_model = models.Repository
    relationship = "content_objects"


class RepositoryVersionList(views.ListAPIView):
    model = models.Repository
    serializer_class = serializers.RepositoryVersionSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.all_versions()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
