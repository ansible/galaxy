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

from __future__ import print_function

import logging
from collections import OrderedDict
from allauth.socialaccount.models import SocialToken
from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.urls import reverse
from django.db.models import Count, Max
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

# TODO move all github interactions to githubapi
# Github
from github import Github
from github.GithubException import GithubException

# rest framework stuff
from rest_framework import status
from rest_framework.authentication import (
    TokenAuthentication, SessionAuthentication
)
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters as drf_filters

from galaxy import constants
from galaxy.accounts.models import CustomUser as User
from galaxy.api.permissions import ModelAccessPermission
from galaxy.api import filters as galaxy_filters
from galaxy.api import serializers
from galaxy.api import tasks
from galaxy.api.views import base_views
from galaxy.main.celerytasks import tasks as celerytasks
from galaxy.main import models
from galaxy.common import version, sanitize_content_name


logger = logging.getLogger(__name__)

__all__ = [
    'ActiveProviderDetail',
    'ActiveProviderList',
    'ApiRootView',
    'ApiV1ReposView',
    'ApiV1RootView',
    'CloudPlatformDetail',
    'CloudPlatformList',
    'ImportTaskDetail',
    'ImportTaskLatestList',
    'ImportTaskList',
    'ImportTaskNotificationList',
    'PlatformDetail',
    'PlatformList',
    'ProviderRootView',
    'RefreshUserRepos',
    'RemoveRole',
    'RoleDependenciesList',
    'RoleDownloads',
    'RoleImportTaskList',
    'RoleImportTaskList',
    'RoleTypes',
    'RoleUsersList',
    'RoleVersionList',
    'StargazerDetail',
    'StargazerList',
    'SubscriptionDetail',
    'SubscriptionList',
    'TagDetail',
    'TagList',
    'TopContributorsList',
]


# -----------------------------------------------------------------------------
# Helper functions


def filter_user_queryset(qs):
    return qs.filter(is_active=True)


def filter_role_queryset(qs):
    return qs.filter(active=True, is_valid=True)


def filter_rating_queryset(qs):
    return qs.filter(
        active=True,
        role__active=True,
        role__is_valid=True,
        owner__is_active=True,
    )

# -----------------------------------------------------------------------------


class ApiRootView(base_views.APIView):
    permission_classes = (AllowAny,)
    view_name = 'REST API'

    def get(self, request, format=None):
        # list supported API versions
        current = reverse('api:api_v1_root_view', args=[])
        data = dict(
            description='GALAXY REST API',
            current_version='v1',
            available_versions=dict(
                v1=current
            ),
            server_version=version.get_package_version('galaxy'),
            version_name=version.get_version_name(),
            team_members=version.get_team_members(),
        )
        return Response(data)


class ApiV1RootView(base_views.APIView):
    permission_classes = (AllowAny,)
    view_name = 'Version 1'

    def get(self, request, format=None):
        # list top level resources
        data = OrderedDict()
        data['cloud_platforms'] = reverse('api:cloud_platform_list')
        data['content'] = reverse('api:content_list')
        data['content_blocks'] = reverse('api:content_block_list')
        data['content_types'] = reverse('api:content_type_list')
        data['imports'] = reverse('api:import_task_list')
        data['latest_imports'] = reverse('api:import_task_latest_list')
        data['me'] = reverse('api:active_user_view')
        data['namespaces'] = reverse('api:namespace_list')
        data['notifications'] = reverse('api:notification_list')
        data['platforms'] = reverse('api:platform_list')
        data['provider_namespaces'] = reverse('api:provider_namespace_list')
        data['providers'] = reverse('api:provider_root_view')
        data['repositories'] = reverse('api:repository_list')
        data['role_types'] = reverse('api:role_types')
        data['roles'] = reverse('api:role_list')
        data['search'] = reverse('api:search_view')
        data['tags'] = reverse('api:tag_list')
        data['users'] = reverse('api:user_list')
        data['surveys'] = reverse('api:community_survey_list')
        data['emails'] = reverse('api:email_list')
        return Response(data)


class ProviderRootView(base_views.APIView):
    """ Provider resources """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        data = OrderedDict()
        data['active'] = reverse('api:active_provider_list')
        data['sources'] = reverse('api:provider_source_list')
        return Response(data)


class ActiveProviderList(base_views.ListAPIView):
    """ Active providers """
    model = models.Provider
    serializer_class = serializers.ProviderSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return self.model.objects.filter(active=True)


class ActiveProviderDetail(base_views.RetrieveAPIView):
    """ Active providers """
    model = models.Provider
    serializer_class = serializers.ProviderSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return self.model.objects.filter(active=True)


class RoleTypes(base_views.APIView):
    permission_classes = (AllowAny,)
    view_name = 'Role Types'

    def get(self, request, format=None):
        roles = [role for role in constants.RoleType.choices()
                 if role[0] in settings.ROLE_TYPES_ENABLED]
        return Response(roles)


class ApiV1ReposView(base_views.APIView):
    permission_classes = (AllowAny,)
    view_name = 'Repos'

    def get(self, request, *args, **kwargs):
        data = OrderedDict()
        data['list'] = reverse('api:repository_list')
        data['refresh'] = reverse('api:refresh_user_repos')
        data['stargazers'] = reverse('api:stargazer_list')
        data['subscriptions'] = reverse('api:subscription_list')
        return Response(data)


class TagList(base_views.ListAPIView):
    model = models.Tag
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        return self.model.objects.filter(active=True)


class TagDetail(base_views.RetrieveAPIView):
    model = models.Tag
    serializer_class = serializers.TagSerializer


class PlatformList(base_views.ListAPIView):
    model = models.Platform
    serializer_class = serializers.PlatformSerializer
    paginate_by = None


class PlatformDetail(base_views.RetrieveAPIView):
    model = models.Platform
    serializer_class = serializers.PlatformSerializer


class CloudPlatformList(base_views.ListAPIView):
    model = models.CloudPlatform
    serializer_class = serializers.CloudPlatformSerializer
    paginate_by = None


class CloudPlatformDetail(base_views.RetrieveAPIView):
    model = models.CloudPlatform
    serializer_class = serializers.CloudPlatformSerializer


class RoleDependenciesList(base_views.SubListAPIView):
    model = models.Content
    serializer_class = serializers.RoleDetailSerializer
    parent_model = models.Content
    relationship = 'dependencies'

    def get_queryset(self):
        qs = super(RoleDependenciesList, self).get_queryset()
        return filter_role_queryset(qs)


class RoleUsersList(base_views.SubListAPIView):
    model = User
    serializer_class = serializers.UserSerializer
    parent_model = models.Content
    relationship = 'created_by'

    def get_queryset(self):
        qs = super(RoleUsersList, self).get_queryset()
        return filter_user_queryset(qs)


class RoleImportTaskList(base_views.ListAPIView):
    model = models.ImportTask
    serializer_class = serializers.ImportTaskSerializer

    def list(self, request, *args, **kwargs):
        id = kwargs.pop('pk')
        try:
            content = models.Content.objects.get(pk=id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        qs = content.repository.import_tasks.select_related(
            'owner',
            'repository',
            'repository__provider_namespace',
            'repository__provider_namespace__provider',
            'repository__provider_namespace__namespace',
        ).all()
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class RoleDownloads(base_views.APIView):

    def post(self, request, pk):
        obj = get_object_or_404(models.Content, pk=pk)
        obj.download_count += 1
        obj.save()
        return Response(status=status.HTTP_201_CREATED)


class RoleVersionList(base_views.ListAPIView):
    model = models.RepositoryVersion
    serializer_class = serializers.RoleVersionSerializer

    def list(self, request, *args, **kwargs):
        id = kwargs.pop('pk')
        try:
            content = models.Content.objects.get(pk=id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        qs = content.repository.versions.all()
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ImportTaskList(base_views.ListCreateAPIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (ModelAccessPermission,)
    model = models.ImportTask
    serializer_class = serializers.ImportTaskSerializer
    filter_backends = (
        galaxy_filters.ActiveOnlyBackend,
        galaxy_filters._FieldLookupBackend,
        drf_filters.SearchFilter,
        galaxy_filters.OrderByBackend,
    )

    def get_queryset(self):
        qs = models.ImportTask.objects.select_related(
            'owner',
            'repository',
            'repository__provider_namespace',
            'repository__provider_namespace__provider',
            'repository__provider_namespace__namespace',
        )
        return qs

    def get_serializer_class(self):
        # NOTE(cutwater): This is for compatibility with ansible-galaxy client.
        if 'id' in self.request.GET:
            return serializers.ImportTaskDetailSerializer
        return super(ImportTaskList, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        github_user = request.GET.get('github_user')
        github_repo = request.GET.get('github_repo')

        qs = self.get_queryset()
        if github_user and github_repo:
            # Support ansible-galaxy <= 2.6
            qs = qs.filter(
                repository__provider_namespace__name=github_user,
                repository__original_name=github_repo)
        else:
            qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        github_user = request.data.get('github_user')
        github_repo = request.data.get('github_repo')
        github_reference = request.data.get('github_reference', '')
        repository_id = request.data.get('repository_id')

        if not repository_id:
            # request received from old client
            if not github_user or not github_repo:
                raise ValidationError({
                    'detail': "Invalid request. "
                              "Expecting github_user and github_repo."
                })

            namespace = models.ProviderNamespace.objects.get(
                provider__name=constants.PROVIDER_GITHUB,
                name=github_user
            )
            if not request.user.is_staff and \
               not namespace.namespace.owners.filter(
                   username=request.user.get_username()):
                # User is not an onwer of the Namespace
                raise PermissionDenied(
                    "You are not an owner of {0}"
                    .format(namespace.namespace.name)
                )

            try:
                repository = models.Repository.objects.get(
                    provider_namespace=namespace,
                    original_name=github_repo
                )
            except ObjectDoesNotExist:
                repository, created = models.Repository.objects.get_or_create(
                    provider_namespace=namespace,
                    name=sanitize_content_name(github_repo),
                    defaults={
                        'is_enabled': False,
                        'original_name': github_repo,
                        'is_new': True
                    }
                )
        else:
            try:
                repository = models.Repository.objects.get(pk=repository_id)
            except ObjectDoesNotExist:
                raise ValidationError({
                    'detail': "Repository {0} not found, or you do not "
                              "have access".format(repository_id)
                })

            if not request.user.is_staff and \
               not repository.provider_namespace.namespace.owners.filter(
                   username=request.user.get_username()):
                # User is not an onwer of the Namespace
                raise PermissionDenied(
                    "You are not an owner of {0}".format(repository.name)
                )

        task = tasks.create_import_task(
            repository, request.user,
            import_branch=github_reference, user_initiated=True)

        serializer = self.get_serializer(instance=task)
        response = {'results': [serializer.data]}
        return Response(response,
                        status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(response))


class ImportTaskDetail(base_views.RetrieveAPIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (ModelAccessPermission,)
    model = models.ImportTask
    serializer_class = serializers.ImportTaskDetailSerializer

    def get_object(self, qs=None):
        obj = super(ImportTaskDetail, self).get_object()
        if not obj.active:
            raise Http404()
        return obj


class ImportTaskNotificationList(base_views.SubListAPIView):
    model = models.Notification
    serializer_class = serializers.NotificationSerializer
    parent_model = models.ImportTask
    relationship = 'notifications'


class ImportTaskLatestList(base_views.ListAPIView):
    """Return the most recent import for each of the user's repositories."""
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    model = models.ImportTask
    serializer_class = serializers.ImportTaskLatestSerializer

    def list(self, request, *args, **kwargs):
        qs = models.ImportTask.objects.filter(
            repository__provider_namespace__namespace__isnull=False
        ).values(
            'repository__provider_namespace__namespace__name',
            'repository__name',
            'repository__id',
        ).order_by(
            'repository__provider_namespace__namespace__name',
            'repository__name'
        ).annotate(last_id=Max('id'))

        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class StargazerList(base_views.ListCreateAPIView):
    model = models.Stargazer
    serializer_class = serializers.StargazerSerializer

    def post(self, request, *args, **kwargs):
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)

        if not github_user or not github_repo:
            raise ValidationError({
                'detail': "Invalid request. "
                          "Missing one or more required values."
            })

        try:
            token = SocialToken.objects.get(
                account__user=request.user, account__provider='github'
            )
        except Exception:
            msg = (
                "Failed to get GitHub token for user {0} "
                "You must first authenticate with GitHub."
                .format(request.user.username)
            )
            raise ValidationError({'detail': msg})

        gh_api = Github(token.token)

        try:
            gh_repo = gh_api.get_repo(github_user + '/' + github_repo)
        except GithubException as e:
            msg = (
                "GitHub API failed to return repo for {0}/{1}. {2} - {3}"
                .format(github_user, github_repo, e.data, e.status)
            )
            raise ValidationError({'detail': msg})

        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            msg = (
                "GitHub API failed to return authorized user. {0} - {1}"
                .format(e.data, e.status)
            )
            raise ValidationError({'detail': msg})

        try:
            gh_user.add_to_starred(gh_repo)
        except GithubException as e:
            msg = (
                "GitHub API failed to add user {0} to stargazers "
                "for {1}/{2}. {3} - {4}"
                .format(request.user.username, github_user, github_repo,
                        e.data, e.status)
            )
            raise ValidationError({'detail': msg})

        repo = models.Repository.objects.get(
            github_user=github_user, github_repo=github_repo
        )
        star = repo.stars.create(owner=request.user)
        repo.stargazers_count = gh_repo.stargazers_count + 1
        repo.save()

        return Response(dict(
            result=dict(
                id=star.id,
                github_user=repo.github_user,
                github_repo=repo.github_repo,
                stargazers_count=repo.stargazers_count)),
            status=status.HTTP_201_CREATED)


class StargazerDetail(base_views.RetrieveUpdateDestroyAPIView):
    model = models.Stargazer
    serializer_class = serializers.StargazerSerializer

    def destroy(self, request, *args, **kwargs):
        obj = super(StargazerDetail, self).get_object()

        try:
            token = SocialToken.objects.get(
                account__user=request.user, account__provider='github'
            )
        except Exception:
            msg = (
                "Failed to connect to GitHub account for Galaxy user {}. "
                "You must first authenticate with Github."
                .format(request.user.username)
            )
            raise ValidationError({'detail': msg})

        gh_api = Github(token.token)

        try:
            gh_repo = gh_api.get_repo(
                obj.role.github_user + '/' + obj.role.github_repo)
        except GithubException as e:
            msg = (
                "GitHub API failed to return repo for {}/{}. {} - {}"
                .format(obj.github_user, obj.github_repo, e.data, e.status)
            )
            raise ValidationError({'detail': msg})

        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            msg = (
                "GitHub API failed to return authorized user. {} - {}"
                .format(e.data, e.status)
            )
            raise ValidationError({'detail': msg})

        try:
            gh_user.remove_from_starred(gh_repo)
        except GithubException as e:
            msg = (
                "GitHub API failed to remove user {} from stargazers "
                "for {}/{}. {} - {}"
                .format(request.user.username, obj.github_user,
                        obj.github_repo, e.data, e.status)
            )
            raise ValidationError({'detail': msg})

        obj.delete()

        repo = models.Repository.objects.get(
            github_user=obj.role.github_user,
            github_repo=obj.role.github_repo,
        )
        repo.stargazers_count = max(0, gh_repo.stargazers_count - 1)
        repo.save()

        return Response(status=status.HTTP_202_ACCEPTED)


class SubscriptionList(base_views.ListCreateAPIView):
    model = models.Subscription
    serializer_class = serializers.SubscriptionSerializer

    def post(self, request, *args, **kwargs):
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)

        if not github_user or not github_repo:
            raise ValidationError({
                'detail': "Invalid request. "
                          "Missing one or more required values."
            })

        try:
            token = SocialToken.objects.get(
                account__user=request.user,
                account__provider='github'
            )
        except Exception:
            msg = (
                "Failed to connect to GitHub account for Galaxy user {}. "
                "You must first authenticate with Github."
                .format(request.user.username)
            )
            raise ValidationError(dict(detail=msg))

        gh_api = Github(token.token)

        try:
            gh_repo = gh_api.get_repo(github_user + '/' + github_repo)
        except GithubException as e:
            msg = (
                "GitHub API failed to return repo for {}/{}. {} - {}"
                .format(github_user, github_repo, e.data, e.status)
            )
            raise ValidationError(dict(detail=msg))

        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            msg = (
                "GitHub API failed to return authorized user. {} - {}"
                .format(e.data, e.status)
            )
            raise ValidationError(dict(detail=msg))

        try:
            gh_user.add_to_subscriptions(gh_repo)
        except GithubException:
            msg = (
                "GitHub API failed to subscribe user {} to for {}/{}"
                .format(request.user.username, github_user, github_repo)
            )
            raise ValidationError(dict(detail=msg))

        new_sub, created = models.Subscription.objects.get_or_create(
            owner=request.user,
            github_user=github_user,
            github_repo=github_repo,
            defaults={
                'owner': request.user,
                'github_user': github_user,
                'github_repo': github_repo
            })

        sub_count = 0
        for s in gh_repo.get_subscribers():
            sub_count += 1   # only way to get subscriber count via pygithub

        repo = models.Repository.objects.get(github_user=github_user,
                                             github_repo=github_repo)
        repo.watchers_count = sub_count
        repo.save()

        return Response(dict(
            result=dict(
                id=new_sub.id,
                github_user=new_sub.github_user,
                github_repo=new_sub.github_repo,
                watchers_count=sub_count
            )
        ), status=status.HTTP_201_CREATED)


class SubscriptionDetail(base_views.RetrieveUpdateDestroyAPIView):
    model = models.Subscription
    serializer_class = serializers.SubscriptionSerializer

    def destroy(self, request, *args, **kwargs):
        obj = super(SubscriptionDetail, self).get_object()

        try:
            token = SocialToken.objects.get(
                account__user=request.user, account__provider='github'
            )
        except Exception:
            msg = (
                "Failed to access GitHub account for Galaxy user {}. "
                "You must first authenticate with GitHub."
                .format(request.user.username)
            )
            raise ValidationError(dict(detail=msg))

        gh_api = Github(token.token)

        try:
            gh_repo = gh_api.get_repo(obj.github_user + '/' + obj.github_repo)
        except GithubException as e:
            msg = (
                "GitHub API failed to return repo for {}/{}. {} - {}"
                .format(obj.github_user, obj.github_repo, e.data, e.status)
            )
            raise ValidationError(dict(detail=msg))

        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            msg = (
                "GitHub API failed to return authorized user. {} - {}"
                .format(e.data, e.status)
            )
            raise ValidationError(dict(detail=msg))

        try:
            gh_user.remove_from_subscriptions(gh_repo)
        except GithubException as e:
            msg = (
                "GitHub API failed to unsubscribe {} from {}/{}. {} - {}"
                .format(request.user.username, obj.github_user,
                        obj.github_repo, e.data, e.status)
            )
            raise ValidationError(dict(detail=msg))

        obj.delete()

        sub_count = 0
        for sub in gh_repo.get_subscribers():
            sub_count += 1   # only way to get subscriber count via pygithub

        repo = models.Repository.objects.get(github_user=obj.github_user,
                                             github_repo=obj.github_repo)
        repo.watchers_count = sub_count
        repo.save()

        result = (
            "unsubscribed {} from {}/{}."
            .format(request.user.username, obj.github_user, obj.github_repo)
        )

        return Response(dict(detail=result), status=status.HTTP_202_ACCEPTED)


class TopContributorsList(base_views.ListAPIView):
    model = models.Content
    serializer_class = serializers.TopContributorsSerializer

    def list(self, request, *args, **kwargs):
        qs = (models.Content.objects.values('namespace')
              .annotate(count=Count('id'))
              .order_by('-count', 'namespace'))

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class RemoveRole(base_views.APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):

        gh_user = request.query_params.get('github_user', None)
        gh_repo = request.query_params.get('github_repo', None)

        if not gh_user or not gh_repo:
            raise ValidationError(dict(detail="Invalid request."))

        if not request.user.is_staff:
            # Verify via GitHub API that user has access to requested role
            try:
                token = SocialToken.objects.get(
                    account__user=request.user, account__provider='github'
                )
            except Exception:
                msg = (
                    "Failed to get Github account for Galaxy user {}. "
                    "You must first authenticate with Github."
                    .format(request.user.username)
                )
                raise ValidationError({'detail': msg})

            gh_api = Github(token.token)

            try:
                ghu = gh_api.get_user()
            except Exception:
                raise ValidationError(
                    {'detail': "Failed to get Github authorized user."}
                )

            allowed = False
            repo_full_name = "{}/{}".format(gh_user, gh_repo)
            for r in ghu.get_repos():
                if r.full_name == repo_full_name:
                    allowed = True
                    continue

            if not allowed:
                msg = (
                    "Galaxy user {0} does not have access to repo {1}"
                    .format(request.user.username, repo_full_name)
                )
                raise ValidationError(dict(detail=msg))

        # User has access. Delete requested role and associated bits.
        response = OrderedDict([
            ('deleted_roles', []),
            ('status', '')
        ])

        roles = models.Content.objects.filter(
            repository__provider_namespace__name=gh_user,
            repository__original_name=gh_repo)
        cnt = len(roles)
        if cnt == 0:
            response['status'] = (
                "Role {}.{} not found. Maybe it was deleted previously?"
                .format(gh_user, gh_repo)
            )
            return Response(response)
        elif cnt == 1:
            response['status'] = "Role {}.{} deleted".format(gh_user, gh_repo)
        else:
            response['status'] = (
                "Deleted {:d} roles associated with {}/{}"
                .format(len(roles), gh_user, gh_repo)
            )

        for role in roles:
            response['deleted_roles'].append({
                "id": role.id,
                "namespace": role.namespace.name,
                "name": role.name,
                "github_user": role.github_user,
                "github_repo": role.github_repo
            })

        repo = models.Repository.objects.get(
            provider_namespace__name=gh_user,
            original_name=gh_repo)

        models.Notification.objects.filter(repository=repo).delete()
        models.Content.objects.filter(repository=repo).delete()
        models.ImportTask.objects.filter(repository=repo).delete()
        repo.delete()

        return Response(response)


class RefreshUserRepos(base_views.APIView):
    """
    Return user GitHub repos directly from GitHub.
    Use to refresh cache for the authenticated user.
    """
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Return a the list of user's repositories directly from GitHub
        try:
            token = SocialToken.objects.get(
                account__user=request.user, account__provider='github'
            )
        except Exception:
            msg = (
                "Failed to connect to GitHub account for Galaxy user {} "
                "You must first authenticate with GitHub."
                .format(request.user.username)
            )
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})

        gh_api = Github(token.token)

        try:
            ghu = gh_api.get_user()
        except Exception:
            msg = "Failed to get GitHub authorized user."
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})
        try:
            user_repos = ghu.get_repos()
        except Exception:
            msg = "Failed to get user repositories from GitHub."
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})

        try:
            celerytasks.refresh_existing_user_repos(token.token, ghu)
        except Exception as exc:
            logger.error("Error: refresh_user_repos - {0}".format(exc))
            raise

        try:
            celerytasks.update_user_repos(user_repos, request.user)
        except Exception as exc:
            logger.error("Error: update_user_repos - {0}".format(exc))
            raise

        qs = request.user.repositories.all()
        serializer = serializers.RepositorySerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
