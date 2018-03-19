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

import base64
import json
import logging

# standard python libraries
import sys
from collections import OrderedDict
from hashlib import sha256
from urlparse import parse_qs

import requests
from OpenSSL.crypto import Error as SignatureError
# OpenSSL
from OpenSSL.crypto import verify, load_publickey, FILETYPE_PEM, X509
# allauth
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialToken
from django.conf import settings
# django stuff
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Count, Max
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime

# TODO move all github interactions to githubapi
# Github
from github import Github
from github.GithubException import GithubException

# rest framework stuff
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from galaxy.accounts.models import CustomUser as User
from galaxy.api.access import check_user_access
from galaxy.api.permissions import ModelAccessPermission
from galaxy.api.serializers import (MeSerializer,
                                    UserListSerializer,
                                    UserDetailSerializer,
                                    SubscriptionSerializer,
                                    StargazerSerializer,
                                    CategorySerializer,
                                    TagSerializer,
                                    PlatformSerializer,
                                    CloudPlatformSerializer,
                                    RoleVersionSerializer,
                                    RepositorySerializer,
                                    TopContributorsSerializer,
                                    NotificationSecretSerializer,
                                    NotificationSerializer,
                                    ImportTaskSerializer,
                                    ImportTaskLatestSerializer,
                                    ProviderSerializer,
                                    RoleDetailSerializer)

from .base_views import (APIView,
                         ListAPIView,
                         ListCreateAPIView,
                         SubListAPIView,
                         RetrieveAPIView,
                         RetrieveUpdateDestroyAPIView)

from galaxy.main.celerytasks.tasks import update_user_repos, refresh_existing_user_repos
from galaxy.worker.tasks import import_repository
from galaxy.main.models import (Platform,
                                CloudPlatform,
                                Category,
                                Tag,
                                Content,
                                ContentType,
                                ImportTask,
                                ContentVersion,
                                NotificationSecret,
                                Notification,
                                Provider,
                                ProviderNamespace,
                                Repository,
                                Subscription,
                                Stargazer)

from galaxy.main import constants
from galaxy.main.utils import camelcase_to_underscore

# local stuff

logger = logging.getLogger(__name__)

__all__ = [
    'ActiveProviderDetail',
    'ActiveProviderList',
    'ApiRootView',
    'ApiV1ReposView',
    'ApiV1RootView',
    'CategoryDetail',
    'CategoryList',
    'CloudPlatformDetail',
    'CloudPlatformList',
    'ImportTaskDetail',
    'ImportTaskLatestList',
    'ImportTaskList',
    'ImportTaskNotificationList',
    'NotificationDetail',
    'NotificationImportsList',
    'NotificationList',
    'NotificationRolesList',
    'NotificationSecretDetail',
    'NotificationSecretList',
    'PlatformDetail',
    'PlatformList',
    'ProviderRootView',
    'RefreshUserRepos',
    'RemoveRole',
    'RoleDependenciesList',
    'RoleDownloads',
    'RoleImportTaskList',
    'RoleNotificationList',
    'RoleTypes',
    'RoleUsersList',
    'RoleVersionsList',
    'StargazerDetail',
    'StargazerList',
    'SubscriptionDetail',
    'SubscriptionList',
    'TagDetail',
    'TagList',
    'TokenView',
    'TopContributorsList',
    'UserDetail',
    'UserList',
    'UserMeList',
    'UserNotificationSecretList',
    'UserRepositoriesList',
    'UserRolesList',
    'UserStarredList',
    'UserSubscriptionList',
]

# --------------------------------------------------------------------------------
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


def create_import_task(
        repository, user,
        import_branch=None, repository_alt_name=None,
        travis_status_url='', travis_build_url=''):
    task = ImportTask.objects.create(
        repository=repository,
        owner=user,
        import_branch=import_branch,
        repository_alt_name=repository_alt_name,
        travis_status_url=travis_status_url,
        travis_build_url=travis_build_url,
        state=ImportTask.STATE_PENDING
    )
    import_repository.delay(task.id)
    return task

# --------------------------------------------------------------------------------


class ApiRootView(APIView):
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
            )
        )
        return Response(data)


class ApiV1RootView(APIView):
    permission_classes = (AllowAny,)
    view_name = 'Version 1'

    def get(self, request, format=None):
        # list top level resources
        data = OrderedDict()
        data['me'] = reverse('api:user_me_list')
        data['users'] = reverse('api:user_list')
        data['roles'] = reverse('api:role_list')
        data['role_types'] = reverse('api:role_types')
        data['categories'] = reverse('api:category_list')
        data['tags'] = reverse('api:tag_list')
        data['platforms'] = reverse('api:platform_list')
        data['cloud_platforms'] = reverse('api:cloud_platform_list')
        data['imports'] = reverse('api:import_task_list')
        data['repositories'] = reverse('api:repository_list')
        data['latest imports'] = reverse('api:import_task_latest_list')
        data['namespaces'] = reverse('api:namespace_list')
        data['notification secrets'] = reverse('api:notification_secret_list')
        data['notifications'] = reverse('api:notification_list')
        data['providers'] = reverse('api:provider_root_view')
        data['provider_namespaces'] = reverse('api:provider_namespace_list')
        data['tokens'] = reverse('api:token')
        data['search'] = reverse('api:search_view')
        data['remove role'] = reverse('api:remove_role')
        return Response(data)


class ProviderRootView(APIView):
    """ Provider resources """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        data = OrderedDict()
        data['active'] = reverse('api:active_provider_list')
        data['sources'] = reverse('api:provider_source_list')
        return Response(data)


class ActiveProviderList(ListAPIView):
    """ Active providers """
    model = Provider
    serializer_class = ProviderSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return self.model.objects.filter(active=True)


class ActiveProviderDetail(RetrieveAPIView):
    """ Active providers """
    model = Provider
    serializer_class = ProviderSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return self.model.objects.filter(active=True)


class RoleTypes(APIView):
    permission_classes = (AllowAny,)
    view_name = 'Role Types'

    def get(self, request, format=None):
        roles = [role for role in constants.RoleType.choices()
                 if role[0] in settings.ROLE_TYPES_ENABLED]
        return Response(roles)


class ApiV1ReposView(APIView):
    permission_classes = (AllowAny,)
    view_name = 'Repos'

    def get(self, request, *args, **kwargs):
        data = OrderedDict()
        data['list'] = reverse('api:repository_list')
        data['refresh'] = reverse('api:refresh_user_repos')
        data['stargazers'] = reverse('api:stargazer_list')
        data['subscriptions'] = reverse('api:subscription_list')
        return Response(data)


class CategoryList(ListAPIView):
    model = Category
    serializer_class = CategorySerializer
    paginate_by = None

    def get_queryset(self):
        return self.model.objects.filter(active=True)


class TagList(ListAPIView):
    model = Tag
    serializer_class = TagSerializer

    def get_queryset(self):
        return self.model.objects.filter(active=True)


class TagDetail(RetrieveAPIView):
    model = Tag
    serializer_class = TagSerializer


class CategoryDetail(RetrieveAPIView):
    model = Category
    serializer_class = CategorySerializer


class PlatformList(ListAPIView):
    model = Platform
    serializer_class = PlatformSerializer
    paginate_by = None


class PlatformDetail(RetrieveAPIView):
    model = Platform
    serializer_class = PlatformSerializer


class CloudPlatformList(ListAPIView):
    model = CloudPlatform
    serializer_class = CloudPlatformSerializer
    paginate_by = None


class CloudPlatformDetail(RetrieveAPIView):
    model = CloudPlatform
    serializer_class = CloudPlatformSerializer


class RoleDependenciesList(SubListAPIView):
    model = Content
    serializer_class = RoleDetailSerializer
    parent_model = Content
    relationship = 'dependencies'

    def get_queryset(self):
        qs = super(RoleDependenciesList, self).get_queryset()
        return filter_role_queryset(qs)


class RoleUsersList(SubListAPIView):
    model = User
    serializer_class = UserDetailSerializer
    parent_model = Content
    relationship = 'created_by'

    def get_queryset(self):
        qs = super(RoleUsersList, self).get_queryset()
        return filter_user_queryset(qs)


class RoleNotificationList(SubListAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    parent_model = Content
    relationship = 'notifications'


class RoleImportTaskList(SubListAPIView):
    model = ImportTask
    serializer_class = ImportTaskSerializer
    parent_model = Content
    relationship = 'import_tasks'


class RoleVersionsList(SubListAPIView):
    model = ContentVersion
    serializer_class = RoleVersionSerializer
    parent_model = Content
    relationship = 'versions'


class RoleDownloads(APIView):

    def post(self, request, pk):
        obj = get_object_or_404(Content, pk=pk)
        obj.download_count += 1
        obj.save()
        return Response(status=status.HTTP_201_CREATED)


class ImportTaskList(ListCreateAPIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (ModelAccessPermission,)
    model = ImportTask
    serializer_class = ImportTaskSerializer

    def get_queryset(self):
        return super(ImportTaskList, self).get_queryset()

    def post(self, request, *args, **kwargs):
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)
        github_reference = request.data.get('github_reference', '')
        alternate_role_name = request.data.get('alternate_role_name', None)

        if not github_user or not github_repo:
            raise ValidationError(
                dict(detail="Invalid request. Expecting github_user and github_repo.")
            )

        repo_name = alternate_role_name or github_repo

        namespace = ProviderNamespace.objects.get(
            provider__name=constants.PROVIDER_GITHUB,
            name=github_user
        )
        repository, created = Repository.objects.get_or_create(
            provider_namespace=namespace,
            name=repo_name,
            defaults={'is_enabled': False,
                      'original_name': github_repo}
        )
        task = create_import_task(
            repository, request.user,
            import_branch=github_reference,
            repository_alt_name=alternate_role_name)
        serializer = self.get_serializer(instance=task)
        response = {'results': [serializer.data]}
        return Response(response,
                        status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(response))


class ImportTaskDetail(RetrieveAPIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (ModelAccessPermission,)
    model = ImportTask
    serializer_class = ImportTaskSerializer

    def get_object(self, qs=None):
        obj = super(ImportTaskDetail, self).get_object()
        if not obj.active:
            raise Http404()
        return obj


class ImportTaskNotificationList(SubListAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    parent_model = ImportTask
    relationship = 'notifications'


class ImportTaskLatestList(ListAPIView):
    """ Return the most recent import for each of the user's repositories """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    model = ImportTask
    serializer_class = ImportTaskLatestSerializer

    def list(self, request, *args, **kwargs):
        qs = ImportTask.objects.filter(
            repository__provider_namespace__namespace__isnull=False,
            repository__provider_namespace__namespace__owners=request.user
        ).values(
            'repository__provider_namespace__namespace__name',
            'repository__name'
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


class UserRepositoriesList(SubListAPIView):
    model = Repository
    serializer_class = RepositorySerializer
    parent_model = User
    relationship = 'repositories'


class UserRolesList(SubListAPIView):
    model = Content
    serializer_class = RoleDetailSerializer
    parent_model = User
    relationship = 'roles'

    def get_queryset(self):
        qs = super(UserRolesList, self).get_queryset()
        return filter_role_queryset(qs)


class UserSubscriptionList(SubListAPIView):
    model = Subscription
    serializer_class = SubscriptionSerializer
    parent_model = User
    relationship = 'subscriptions'


class UserStarredList(SubListAPIView):
    model = Stargazer
    serializer_class = StargazerSerializer
    parent_model = User
    relationship = 'starred'


class UserNotificationSecretList(SubListAPIView):
    model = NotificationSecret
    serializer_class = NotificationSecretSerializer
    parent_model = User
    relationship = 'notification_secrets'


class StargazerList(ListCreateAPIView):
    model = Stargazer
    serializer_class = StargazerSerializer

    def post(self, request, *args, **kwargs):
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)

        if not github_user or not github_repo:
            raise ValidationError(dict(detail="Invalid request. Missing one or more required values."))

        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            msg = "Failed to get GitHub token for user {0} ".format(request.user.username) + \
                  "You must first authenticate with GitHub."
            raise ValidationError(dict(detail=msg))

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except GithubException as e:
            msg = "Failed to connect to GitHub API. This is most likely a temporary error, " + \
                  "please try again in a few minutes. {0} - {1}".format(e.data, e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_repo = gh_api.get_repo(github_user + '/' + github_repo)
        except GithubException as e:
            msg = "GitHub API failed to return repo for {0}/{1}. {2} - {3}".format(github_user,
                                                                                   github_repo,
                                                                                   e.data,
                                                                                   e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            msg = "GitHub API failed to return authorized user. {0} - {1}".format(e.data, e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_user.add_to_starred(gh_repo)
        except GithubException as e:
            msg = "GitHub API failed to add user {0} to stargazers ".format(request.user.github_user) + \
                "for {0}/{1}. {2} - {3}".format(github_user, github_repo, e.data, e.status)
            raise ValidationError(dict(detail=msg))

        repo = Repository.objects.get(github_user=github_user,
                                      github_repo=github_repo)
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


class StargazerDetail(RetrieveUpdateDestroyAPIView):
    model = Stargazer
    serializer_class = StargazerSerializer

    def destroy(self, request, *args, **kwargs):
        obj = super(StargazerDetail, self).get_object()

        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            msg = "Failed to connect to GitHub account for Galaxy user {0}. ".format(request.user.username) + \
                  "You must first authenticate with Github."
            raise ValidationError(dict(detail=msg))
        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except GithubException as e:
            msg = "Failed to connect to GitHub API. This is most likely a temporary " + \
                "error, please try again in a few minutes. {0} - {1}".format(e.data, e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_repo = gh_api.get_repo(
                obj.role.github_user + '/' + obj.role.github_repo)
        except GithubException as e:
            msg = "GitHub API failed to return repo for {0}/{1}. {2} - {3}".format(obj.github_user,
                                                                                   obj.github_repo,
                                                                                   e.data,
                                                                                   e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            msg = "GitHub API failed to return authorized user. {0} - {1}".format(e.data, e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_user.remove_from_starred(gh_repo)
        except GithubException as e:
            msg = "GitHub API failed to remove user {0} from stargazers ".format(request.user.github_user) + \
                "for {0}/{1}. {2} - {3}".format(obj.github_user, obj.github_repo, e.data, e.status)
            raise ValidationError(dict(detail=msg))

        obj.delete()

        repo = Repository.objects.get(github_user=obj.role.github_user,
                                      github_repo=obj.role.github_repo)
        repo.stargazers_count = max(0, gh_repo.stargazers_count - 1)
        repo.save()

        return Response(status=status.HTTP_202_ACCEPTED)


class SubscriptionList(ListCreateAPIView):
    model = Subscription
    serializer_class = SubscriptionSerializer

    def post(self, request, *args, **kwargs):
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)

        if not github_user or not github_repo:
            raise ValidationError(dict(detail="Invalid request. Missing one or more required values."))

        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            msg = "Failed to connect to GitHub account for Galaxy user {0}. ".format(request.user.username) + \
                  "You must first authenticate with Github."
            raise ValidationError(dict(detail=msg))

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except GithubException as e:
            msg = "Failed to connect to GitHub API. This is most likely a temporary error, please try " + \
                  "again in a few minutes. {0} - {1}".format(e.data, e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_repo = gh_api.get_repo(github_user + '/' + github_repo)
        except GithubException as e:
            msg = "GitHub API failed to return repo for {0}/{1}. {2} - {3}".format(github_user,
                                                                                   github_repo,
                                                                                   e.data,
                                                                                   e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            msg = "GitHub API failed to return authorized user. {0} - {1}".format(e.data, e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_user.add_to_subscriptions(gh_repo)
        except GithubException as e:
            msg = "GitHub API failed to subscribe user {0} to for {1}/{2}".format(request.user.github_user,
                                                                                  github_user,
                                                                                  github_repo)
            raise ValidationError(dict(detail=msg))

        new_sub, created = Subscription.objects.get_or_create(
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

        repo = Repository.objects.get(github_user=github_user,
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


class SubscriptionDetail(RetrieveUpdateDestroyAPIView):
    model = Subscription
    serializer_class = SubscriptionSerializer

    def destroy(self, request, *args, **kwargs):
        obj = super(SubscriptionDetail, self).get_object()

        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            msg = "Failed to access GitHub account for Galaxy user {0}. ".format(request.user.username) + \
                  "You must first authenticate with GitHub."
            raise ValidationError(dict(detail=msg))

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except GithubException as e:
            msg = "Failed to connect to GitHub API. This is most likely a temporary error, " + \
                  "please try again in a few minutes. {0} - {1}".format(e.data, e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_repo = gh_api.get_repo(obj.github_user + '/' + obj.github_repo)
        except GithubException as e:
            msg = "GitHub API failed to return repo for {0}/{1}. {2} - {3}".format(obj.github_user,
                                                                                   obj.github_repo,
                                                                                   e.data,
                                                                                   e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            msg = "GitHub API failed to return authorized user. {0} - {1}".format(e.data, e.status)
            raise ValidationError(dict(detail=msg))

        try:
            gh_user.remove_from_subscriptions(gh_repo)
        except GithubException as e:
            msg = "GitHub API failed to unsubscribe {0} from {1}/{2}. {3} - {4}".format(request.user.github_user,
                                                                                        obj.github_user,
                                                                                        obj.github_repo,
                                                                                        e.data,
                                                                                        e.status)
            raise ValidationError(dict(detail=msg))

        obj.delete()

        sub_count = 0
        for sub in gh_repo.get_subscribers():
            sub_count += 1   # only way to get subscriber count via pygithub

        repo = Repository.objects.get(github_user=obj.github_user,
                                      github_repo=obj.github_repo)
        repo.watchers_count = sub_count
        repo.save()

        result = "unsubscribed {0} from {1}/{2}.".format(request.user.github_user,
                                                         obj.github_user,
                                                         obj.github_repo)

        return Response(dict(detail=result), status=status.HTTP_202_ACCEPTED)


class NotificationSecretList(ListCreateAPIView):
    '''
    Integration tokens.
    '''
    model = NotificationSecret
    serializer_class = NotificationSecretSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, ModelAccessPermission,)

    def list(self, request, *args, **kwargs):
        # only list secrets belonging to the authenticated user
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        secret = request.data.get('secret', None)
        source = request.data.get('source', None)
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)

        if not secret or not source or not github_user or not github_repo:
            raise ValidationError(dict(detail="Invalid request. Missing one or more required values."))

        if source not in ['github', 'travis']:
            raise ValidationError(dict(detail="Invalid source value. Expecting one of: [github, travis]"))

        if source == 'travis':
            secret = sha256(github_user + '/' + github_repo + secret).hexdigest()

        secret, create = NotificationSecret.objects.get_or_create(
            source=source,
            github_user=github_user,
            github_repo=github_repo,
            defaults={
                'owner': request.user,
                'source': source,
                'secret': secret,
                'github_user': github_user,
                'github_repo': github_repo
            }
        )

        if not create:
            msg = "Duplicate key. An integration for {0} {1} {2} already exists.".format(source,
                                                                                         github_user,
                                                                                         github_repo)
            raise ValidationError(dict(detail=msg))

        serializer = self.get_serializer(instance=secret)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class NotificationSecretDetail(RetrieveUpdateDestroyAPIView):
    model = NotificationSecret
    serializer_class = NotificationSecretSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, ModelAccessPermission,)

    def put(self, request, *args, **kwargs):
        source = request.data.get('source', None)
        secret = request.data.get('secret', None)
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)

        if not secret or not source or not github_user or not github_repo:
            raise ValidationError(dict(detail="Invalid request. Missing one or more required values."))

        if source not in ['github', 'travis']:
            raise ValidationError(dict(detail="Invalid source value. Expecting one of: [github, travis]"))

        instance = self.get_object()

        if source == 'travis':
            secret = sha256(github_user + '/' + github_repo + secret).hexdigest()

        try:
            instance.source = source
            instance.secret = secret
            instance.github_user = github_user
            instance.github_repo = github_repo
            instance.save()
        except IntegrityError:
            msg = "An integration for {0} {1} {2} already exists.".format(source, github_user, github_repo)
            raise ValidationError(dict(detail=msg))

        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, *args, **kwargs):
        obj = super(NotificationSecretDetail, self).get_object()
        obj.delete()
        return Response(dict(detail="Requested secret deleted."),
                        status=status.HTTP_202_ACCEPTED)


class NotificationList(ListCreateAPIView):
    model = Notification
    serializer_class = NotificationSerializer

    def post(self, request, *args, **kwargs):

        signature = self._get_signature(request)
        json_payload = parse_qs(request.body)['payload'][0]

        slug = request.META.get('HTTP_TRAVIS_REPO_SLUG')
        if not slug:
            msg = "Notification error: expected TRAVIS_REPO_SLUG header"
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})
        github_user, github_repo = slug.split('/', 1)
        owner = self._get_owner(github_user)

        try:
            public_key = self._get_travis_public_key()
        except requests.Timeout:
            msg = "Notification error: Timeout attempting to retrieve Travis CI public key"
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})
        except requests.RequestException as e:
            msg = "Notification error: Failed to retrieve Travis CI public key. %s" % e.message
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})
        try:
            self._check_authorized(signature, public_key, json_payload)
        except SignatureError:
            msg = "Notification error: Authorization failed"
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})

        payload = json.loads(json_payload)
        request_branch = payload['branch']
        travis_status_url = "https://travis-ci.org/%s/%s.svg?branch=%s" % (github_user, github_repo, request_branch)

        notification = Notification.objects.create(
            owner=owner,
            source='travis',
            github_branch=request_branch,
            travis_build_url=payload.get('build_url'),
            travis_status=payload.get('status_message'),
            commit_message=payload.get('message'),
            committed_at=parse_datetime(payload['committed_at']) if payload.get('committed_at') else timezone.now(),
            commit=payload['commit']
        )

        repository, _ = Repository.objects.get_or_create(
            github_user=github_user,
            github_repo=github_repo,
            defaults={'is_enabled': False,
                      'original_name': github_repo})

        role, _ = Content.objects.update_or_create(
            # FIXME(cutwater): Use in-memory cache for content types
            content_type=ContentType.get(constants.ContentType.ROLE),
            repository=repository,
            active=True,
            defaults={
                'namespace': github_user,
                'name': github_repo,
                'github_default_branch': 'master',
                'travis_status_url': travis_status_url,
                'travis_build_url': payload['build_url'],
                'is_valid': False,
            }
        )
        notification.roles.add(role)

        task = create_import_task(
            role.repository, owner,
            travis_status_url=travis_status_url,
            travis_build_url=payload['build_url'])
        notification.imports.add(task)
        notification.save()

        serializer = self.get_serializer(instance=notification)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def _check_authorized(self, signature, public_key, payload):
        """
        Convert the PEM encoded public key to a format palatable for pyOpenSSL,
        then verify the signature
        """
        pkey_public_key = load_publickey(FILETYPE_PEM, public_key)
        certificate = X509()
        certificate.set_pubkey(pkey_public_key)
        verify(certificate, signature, payload, str('sha1'))

    def _get_signature(self, request):
        """
        Extract the raw bytes of the request signature provided by travis
        """
        signature = request.META['HTTP_SIGNATURE']
        return base64.b64decode(signature)

    def _get_travis_public_key(self):
        """
        Returns the PEM encoded public key from the Travis CI /config endpoint
        """
        response = requests.get(settings.TRAVIS_CONFIG_URL, timeout=10.0)
        response.raise_for_status()
        return response.json()['config']['notifications']['webhook']['public_key']

    def _get_owner(self, github_user):
        owner = None
        try:
            owner = User.objects.get(github_user=github_user)
        except User.DoesNotExist:
            pass
        if not owner:
            try:
                owner = User.objects.get(
                    username=settings.GITHUB_TASK_USERS[0])
            except User.DoesNotExist:
                msg = "Notification error: Galaxy task user not found"
                logger.error(msg)
                return HttpResponseBadRequest({'detail': msg})
        return owner


class NotificationDetail(RetrieveAPIView):
    model = Notification
    serializer_class = NotificationSerializer


class NotificationRolesList(SubListAPIView):
    model = Content
    serializer_class = RoleDetailSerializer
    parent_model = Notification
    relationship = 'roles'

    def get_queryset(self):
        qs = super(NotificationRolesList, self).get_queryset()
        return qs


class NotificationImportsList(SubListAPIView):
    model = ImportTask
    serializer_class = ImportTaskSerializer
    parent_model = Notification
    relationship = 'imports'

    def get_queryset(self):
        qs = super(NotificationImportsList, self).get_queryset()
        return qs


class UserDetail(RetrieveAPIView):
    model = User
    serializer_class = UserDetailSerializer

    def update_filter(self, request, *args, **kwargs):
        ''' make sure non-read-only fields that can only be edited by admins, are only edited by admins '''
        obj = User.objects.get(pk=kwargs['pk'])
        can_change = check_user_access(request.user, User, 'change', obj, request.data)
        can_admin = check_user_access(request.user, User, 'admin', obj, request.data)
        if can_change and not can_admin:
            admin_only_edit_fields = ('full_name', 'username', 'is_active', 'is_superuser')
            changed = {}
            for field in admin_only_edit_fields:
                left = getattr(obj, field, None)
                right = request.data.get(field, None)
                if left is not None and right is not None and left != right:
                    changed[field] = (left, right)
            if changed:
                raise PermissionDenied('Cannot change %s' % ', '.join(changed.keys()))

    def get_object(self, qs=None):
        obj = super(UserDetail, self).get_object()
        if not obj.is_active:
            raise Http404()
        return obj


class UserList(ListAPIView):
    model = User
    serializer_class = UserListSerializer

    def get_queryset(self):
        qs = super(UserList, self).get_queryset()
        return filter_user_queryset(qs)


class TopContributorsList(ListAPIView):
    model = Content
    serializer_class = TopContributorsSerializer

    def list(self, request, *args, **kwargs):
        qs = (Content.objects.values('namespace')
              .annotate(count=Count('id'))
              .order_by('-count', 'namespace'))

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class UserMeList(RetrieveAPIView):
    model = User
    serializer_class = MeSerializer
    view_name = 'Me'

    def get_object(self):
        try:
            obj = self.model.objects.get(pk=self.request.user.pk)
        except:
            obj = AnonymousUser()
        return obj


class RemoveRole(APIView):
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
                token = SocialToken.objects.get(account__user=request.user, account__provider='github')
            except:
                msg = "Failed to get Github account for Galaxy user {0}. ".format(request.user.username) + \
                      "You must first authenticate with Github."
                raise ValidationError(dict(detail=msg))

            try:
                gh_api = Github(token.token)
                gh_api.get_api_status()
            except GithubException as e:
                msg = "Failed to connect to GitHub API. This is most likely a temporary error, " + \
                      "please try again in a few minutes. {0} - {1}".format(e.data, e.status)
                raise ValidationError(dict(detail=msg))

            try:
                ghu = gh_api.get_user()
            except:
                raise ValidationError(dict(detail="Failed to get Github authorized user."))

            allowed = False
            repo_full_name = "%s/%s" % (gh_user, gh_repo)
            for r in ghu.get_repos():
                if r.full_name == repo_full_name:
                    allowed = True
                    continue

            if not allowed:
                msg = "Galaxy user {0} does not have access to repo {1}".format(
                    request.user.username, repo_full_name)
                raise ValidationError(dict(detail=msg))

        # User has access. Delete requested role and associated bits.
        response = OrderedDict([
            ('deleted_roles', []),
            ('status', '')
        ])

        roles = Content.objects.filter(
            repository__provider_namespace__name=gh_user,
            repository__name=gh_repo)
        cnt = len(roles)
        if cnt == 0:
            response['status'] = "Role %s.%s not found. Maybe it was deleted previously?" % (gh_user, gh_repo)
            return Response(response)
        elif cnt == 1:
            response['status'] = "Role %s.%s deleted" % (gh_user, gh_repo)
        else:
            response['status'] = "Deleted %d roles associated with %s/%s" % (len(roles), gh_user, gh_repo)

        for role in roles:
            response['deleted_roles'].append({
                "id": role.id,
                "namespace": role.namespace.name,
                "name": role.name,
                "github_user": role.github_user,
                "github_repo": role.github_repo
            })

            for notification in role.notifications.all():
                notification.delete()

        # Update the repository cache
        repo = Repository.objects.get(
            provider_namespace__name=gh_user,
            name=gh_repo)
        repo.is_enabled = False
        repo.save()

        Content.objects.filter(repository=repo).delete()
        ImportTask.objects.filter(repository=repo).delete()

        return Response(response)


class RefreshUserRepos(APIView):
    '''
    Return user GitHub repos directly from GitHub. Use to refresh cache for the authenticated user.
    '''
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Return a the list of user's repositories directly from GitHub
        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            msg = "Failed to connect to GitHub account for Galaxy user {0} ".format(request.user.username) + \
                  "You must first authenticate with GitHub."
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except GithubException as e:
            msg = "Failed to connect to GitHub API. This is most likely a temporary error, " + \
                  "please try again in a few minutes. {0} - {1}".format(e.data, e.status)
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})

        try:
            ghu = gh_api.get_user()
        except:
            msg = "Failed to get GitHub authorized user."
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})
        try:
            user_repos = ghu.get_repos()
        except:
            msg = "Failed to get user repositories from GitHub."
            logger.error(msg)
            return HttpResponseBadRequest({'detail': msg})

        try:
            refresh_existing_user_repos(token.token, ghu)
        except Exception as exc:
            logger.error("Error: refresh_user_repos - {0}".format(exc.message))
            raise

        try:
            update_user_repos(user_repos, request.user)
        except Exception as exc:
            logger.error("Error: update_user_repos - {0}".format(exc.message))
            raise

        qs = request.user.repositories.all()
        serializer = RepositorySerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    '''
    Allows ansible-galaxy CLI to retrieve an auth token
    '''
    def post(self, request, *args, **kwargs):

        gh_user = None
        user = None
        token = None
        github_token = request.data.get('github_token', None)

        if github_token is None:
            raise ValidationError(dict(detail="Invalid request."))

        try:
            git_status = requests.get(settings.GITHUB_SERVER)
            git_status.raise_for_status()
        except:
            raise ValidationError(dict(detail="Error accessing GitHub API. Please try again later."))

        try:
            header = dict(Authorization='token ' + github_token)
            gh_user = requests.get(settings.GITHUB_SERVER + '/user', headers=header)
            gh_user.raise_for_status()
            gh_user = gh_user.json()
            if hasattr(gh_user, 'message'):
                raise ValidationError(dict(detail=gh_user['message']))
        except:
            raise ValidationError(dict(detail="Error accessing GitHub with provided token."))

        if SocialAccount.objects.filter(provider='github', uid=gh_user['id']).count() > 0:
            user = SocialAccount.objects.get(provider='github', uid=gh_user['id']).user
        else:
            msg = "Galaxy user not found. You must first log into Galaxy using your GitHub account."
            raise ValidationError(dict(detail=msg))

        if Token.objects.filter(user=user).count() > 0:
            token = Token.objects.filter(user=user)[0]
        else:
            token = Token.objects.create(user=user)
            token.save()
        result = dict(token=token.key, username=user.username)
        return Response(result, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------
# Create view functions for all of the class-based views to simplify inclusion
# in URL patterns and reverse URL lookups, converting CamelCase names to
# lowercase_with_underscore (e.g. MyView.as_view() becomes my_view).
this_module = sys.modules[__name__]
for attr, value in locals().items():
    if isinstance(value, type) and issubclass(value, APIView):
        name = camelcase_to_underscore(attr)
        view = value.as_view()
        setattr(this_module, name, view)
