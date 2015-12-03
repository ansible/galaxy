# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# standard python libraries
import sys
import math
import requests
import re
import json
from hashlib import sha256

# Github
from github import Github, AuthenticatedUser
from github.GithubException import GithubException

# rest framework stuff
from rest_framework import filters
from rest_framework import mixins
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

# django stuff
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.db.models import F, Count, Avg, Prefetch, Max
from django.http import Http404
from django.utils.datastructures import SortedDict
from django.apps import apps
from django.utils.dateparse import parse_datetime

#allauth
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialToken

# haystack
from drf_haystack.viewsets import HaystackViewSet
from drf_haystack.filters import HaystackAutocompleteFilter
from galaxy.api.filters import HaystackFilter
from haystack.query import SearchQuerySet

# elasticsearch dsl
from elasticsearch_dsl import Search, Q

# local stuff
from galaxy.api.aggregators import *
from galaxy.api.access import *
from galaxy.api.base_views import *
from galaxy.api.permissions import *
from galaxy.api.serializers import *
from galaxy.main.models import *
from galaxy.main.utils import camelcase_to_underscore
from galaxy.api.permissions import ModelAccessPermission
from galaxy.main.celerytasks.tasks import import_role, manage_user_repos


#--------------------------------------------------------------------------------
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

def annotate_user_queryset(qs):
    return qs.annotate(
               num_ratings = Count('ratings', distinct=True),
               # num_roles = Count('roles', distinct=True),
               avg_rating = AvgWithZeroForNull('ratings__score'),
               # avg_role_score = AvgWithZeroForNull('roles__average_score'),
           )

def annotate_role_queryset(qs):
    return qs.annotate(
               num_ratings = Count('ratings', distinct=True),
               average_score = AvgWithZeroForNull('ratings__score'),
               avg_reliability   = AvgWithZeroForNull('ratings__reliability'),
               avg_documentation = AvgWithZeroForNull('ratings__documentation'),
               avg_code_quality  = AvgWithZeroForNull('ratings__code_quality'),
               avg_wow_factor    = AvgWithZeroForNull('ratings__wow_factor'),
           )

def create_import_task(github_user, github_repo, github_branch, role, user):
    task = ImportTask.objects.create(
        github_user         = github_user,
        github_repo         = github_repo,
        github_reference    = github_branch,
        alternate_role_name = '',
        role        = role,
        owner       = user,
        state       = 'PENDING'
    )
    import_role.delay(task.id)
    return task

#--------------------------------------------------------------------------------


class ApiRootView(APIView):
    permission_classes = (AllowAny,)
    view_name = 'REST API'

    def get(self, request, format=None):
        ''' list supported API versions '''
        current = reverse('api:api_v1_root_view', args=[])
        data = dict(
            description = 'GALAXY REST API',
            current_version = 'v1', 
            available_versions = dict(
                v1 = current,
            )
        )
        return Response(data)

class ApiV1RootView(APIView):
    permission_classes = (AllowAny,)
    view_name = 'Version 1'
    def get(self, request, format=None):
        ''' list top level resources '''
        data = SortedDict()
        # data['me']          = reverse('api:user_me_list')
        data['users']       = reverse('api:user_list')
        data['roles']       = reverse('api:role_list')
        data['categories']  = reverse('api:category_list')
        data['tags']        = reverse('api:tag_list')
        data['platforms']   = reverse('api:platform_list')
        # data['ratings']     = reverse('api:rating_list')
        data['imports']     = reverse('api:import_task_list')
        data['repos']                = reverse('api:repos_view')
        data['latest impoorts']      = reverse('api:import_task_latest_list')
        data['notification secrets'] = reverse('api:notification_secret_list')
        data['notifications']        = reverse('api:notification_list')
        data['tokens']               = reverse('api:token')
        data['search']               = reverse('api:search_view')
        data['remove role']          = reverse('api:remove_role')
        return Response(data)

class ApiV1SearchView(APIView):
    permission_classes = (AllowAny,)
    view_name = 'Search'
    def get(self, request, *args, **kwargs):
        data = OrderedDict()
        data['platforms'] = reverse('api:platforms_search_view')
        data['roles'] = reverse('api:search-roles-list')
        data['tags'] = reverse('api:tags_search_view')
        data['users'] = reverse('api:user_search_view')
        data['faceted_platforms'] = reverse('api:faceted_platforms_view')
        data['faceted_tags'] = reverse('api:faceted_tags_view')
        data['top_contributors'] = reverse('api:top_contributors_list')
        return Response(data)

class ApiV1ReposView(APIView):
    permission_classes = (AllowAny,)
    view_name = 'Repos'
    def get(self, request, *args, **kwargs):
        data = OrderedDict()
        data['list']           = reverse('api:repository_list')
        data['refresh']        = reverse('api:refresh_user_repos')
        data['stargazers']     = reverse('api:stargazer_list')
        data['subscriptions']  = reverse('api:subscription_list')
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

class RoleDependenciesList(SubListAPIView):
    model = Role
    serializer_class = RoleDetailSerializer
    parent_model = Role
    relationship = 'dependencies'

    def get_queryset(self):
        qs = super(RoleDependenciesList, self).get_queryset()
        return filter_role_queryset(qs)

class RoleUsersList(SubListAPIView):
    model = User
    serializer_class = UserDetailSerializer
    parent_model = Role
    relationship = 'created_by'

    def get_queryset(self):
        qs = super(RoleUsersList, self).get_queryset()
        return annotate_user_queryset(filter_user_queryset(qs))

class RoleImportTaskList(SubListAPIView):
    model = ImportTask
    serializer_class = ImportTaskSerializer
    parent_model = Role
    relationship = 'import_tasks'

    def get_queryset(self):
        return super(RoleImportTaskList, self).get_queryset()

class RoleVersionsList(SubListAPIView):
    model = RoleVersion
    serializer_class = RoleVersionSerializer
    parent_model = Role
    relationship = 'versions'

class RoleList(ListAPIView):
    model = Role
    serializer_class = RoleListSerializer
    throttle_scope = 'download_count'

    def list(self, request, *args, **kwargs):
        if request.query_params.get('owner__username', None) and request.query_params.get('name', None):
            req_namespace = request.query_params['owner__username']
            req_name = request.query_params['name']
            qs = self.get_queryset()
            qs = qs.filter(namespace=req_namespace,name=req_name)
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_pagination_serializer(page)
            else:
                serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        return super(RoleList, self).list(self, request, *args, **kwargs)
        
    def get_queryset(self):
        qs = super(RoleList, self).get_queryset()
        qs = qs.prefetch_related('platforms', 'tags', 'versions', 'dependencies')
        return filter_role_queryset(qs)

class RoleDetail(RetrieveAPIView):
    model = Role
    serializer_class = RoleDetailSerializer

    
    def get_object(self, qs=None):
        obj = super(RoleDetail, self).get_object()
        if not obj.is_valid or not obj.active:
            raise Http404()
        return obj

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
        
        if not github_user or not github_repo:
            raise ValidationError({ "detail": "Invalid request. Expecting github_user and github_repo." })
        
        response = {}
        response['results'] = []
        if Role.objects.filter(github_user=github_user,github_repo=github_repo,active=True).count() > 1:
            # multiple roles match github_user/github_repo
            for role in Role.objects.filter(github_user=github_user,github_repo=github_repo,active=True):
                task = create_import_task(github_user, github_repo, github_reference, role, request.user)
                import_role.delay(task.id)
                serializer = self.get_serializer(instance=task)
                response['results'].append(serializer.data)
        else:
            role, created = Role.objects.get_or_create(github_user=github_user,github_repo=github_repo, active=True,
                defaults={
                    'namespace':   github_user,
                    'name':        github_repo,
                    'github_user': github_user,
                    'github_repo': github_repo,
                    'is_valid':    False,
                }
            )
            task = create_import_task(github_user, github_repo, github_reference, role, request.user)
            serializer = self.get_serializer(instance=task)
            response['results'].append(serializer.data)
        return Response(response, status=status.HTTP_201_CREATED, headers=self.get_success_headers(response))
    
class ImportTaskDetail(RetrieveAPIView):
    model = ImportTask
    serializer_class = ImportTaskSerializer

    def get_object(self, qs=None):
        obj = super(ImportTaskDetail, self).get_object()
        if not obj.active:
            raise Http404()
        return obj

class ImportTaskLatestList(ListAPIView):
    model = ImportTask
    serializer_class = ImportTaskLatestSerializer

    def get_queryset(self):
        return ImportTask.objects.values('owner_id','github_user','github_repo').annotate(last_id=Max('id')).order_by('owner_id','github_user','github_repo')

class UserRepositoriesList(SubListAPIView):
    model = Repository
    serializer_class = RepositorySerializer
    parent_model = User
    relationship = 'repositories'

class UserRolesList(SubListAPIView):
    model = Role
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
            raise ValidationError({ "detail": "Invalid request. Missing one or more required values." })

        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            raise ValidationError({"detail": "Failed to connect to Github account for Galaxy user %s. You must first " +
                "authenticate with Github." % request.user.username })

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except GithubException as e:
            raise ValidationError({"detail": "Failed to connect to Github API. This is most likely a temporary " +
                "error, please try again in a few minutes. %s" % e.status})

        try:
            gh_repo = gh_api.get_repo(github_user + '/' + github_repo)
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to return repo for %s/%s. %s - %s" %
                (github_user, github_repo, e.data, e.status)})
        
        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to return authorized user. %s - %s" % 
                (e.data, e.status)})

        try:
            gh_user.add_to_starred(gh_repo)
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to add user %s to stargazers for %s/%s. %s - %s" %
                (request.user.github_user, github_user, github_repo, e.data, e.status)})
        
        new_star, created = Stargazer.objects.get_or_create(owner=request.user,github_user=github_user,github_repo=github_repo,
            defaults={
                'owner': request.user,
                'github_user': github_user,
                'github_repo': github_repo
            })

        star_count = gh_repo.stargazers_count + 1
        
        for role in Role.objects.filter(github_user=github_user,github_repo=github_repo):
            role.stargazers_count = star_count
            role.save()
        
        return Response({
            'result': {
                'id': new_star.id,
                'github_user': new_star.github_user,
                'github_repo': new_star.github_repo,
                'stargazers_count': star_count
            }
        }, status=status.HTTP_201_CREATED)

class StargazerDetail(RetrieveUpdateDestroyAPIView):
    model = Stargazer
    serializer_class = StargazerSerializer

    def destroy(self, request, *args, **kwargs):
        obj = super(StargazerDetail, self).get_object()

        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            raise ValidationError({"detail": "Failed to connect to GitHub account for Galaxy user %s. You must first authenticate with Github." % request.user.username })

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except GithubException as e:
            raise ValidationError({"detail": "Failed to connect to GitHub API. This is most likely a temporary " +
                "error, please try again in a few minutes. %s - %s" % (e.data, e.status)})
    
        try:
            gh_repo = gh_api.get_repo(obj.github_user + '/' + obj.github_repo)
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to return repo for %s/%s. %s - %s" %
                (obj.github_user, obj.github_repo, e.data, e.status)})
        
        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to return authorized user. %s - %s" %
                (e.data, e.status)})

        try:
            gh_user.remove_from_starred(gh_repo)
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to remove user %s from stargazers for %s/%s. %s - %s" %
                (request.user.github_user, obj.github_user, obj.github_repo, e.data, e.status)})
        
        obj.delete()

        star_count = gh_repo.stargazers_count - 1 if gh_repo.stargazers_count > 1 else 0

        for role in Role.objects.filter(github_user=obj.github_user,github_repo=obj.github_repo):
            role.stargazers_count = star_count
            role.save()
        
        return Response({ "detail": "%s removed from stargazers for %s/%s." % 
            (request.user.github_user, obj.github_user, obj.github_repo)}, status=status.HTTP_202_ACCEPTED)

class SubscriptionList(ListCreateAPIView):
    model = Subscription
    serializer_class = SubscriptionSerializer

    def post(self, request, *args, **kwargs):
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)

        if not github_user or not github_repo:
            raise ValidationError({ "detail": "Invalid request. Missing one or more required values." })

        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            raise ValidationError({"detail": "Failed to connect to GitHub account for Galaxy user %s. You must first authenticate with Github." % 
                request.user.username })

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except GithubException as e:
            raise ValidationError({"detail": "Failed to connect to GitHub API. This is most likely a temporary error, please try again in a few minutes. %s - %s" % 
                (e.data,e.status)})

    
        try:
            gh_repo = gh_api.get_repo(github_user + '/' + github_repo)
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to return repo for %s/%s. %s - %s" % 
                (github_user, github_repo,e.data,e.status)})
        
        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            print "GitHub API: %s - %s" % (e.data, e.status)
            raise ValidationError({"detail": "GitHub API failed to return authorized user. %s - %s" %
                (e.data,e.status)})

        try:
            gh_user.add_to_subscriptions(gh_repo)
        except GithubException as e:
            print "GitHub API: %s - %s" % (e.data, e.status)
            raise ValidationError({"detail": "GitHub API failed to subscribe user %s to for %s/%s" %
                (request.user.github_user, github_user, github_repo)})
        
        new_sub, created = Subscription.objects.get_or_create(owner=request.user,github_user=github_user,github_repo=github_repo,
            defaults={
                'owner': request.user,
                'github_user': github_user,
                'github_repo': github_repo
            })

        sub_count = 0
        for s in gh_repo.get_subscribers():
            sub_count += 1   # only way to get subscriber count via pygithub
        
        for role in Role.objects.filter(github_user=github_user,github_repo=github_repo):
            role.watchers_count = sub_count
            role.save()
        
        return Response({
            'result': {
                'id': new_sub.id,
                'github_user': new_sub.github_user,
                'github_repo': new_sub.github_repo,
                'watchers_count': sub_count
            }
        }, status=status.HTTP_201_CREATED)

class SubscriptionDetail(RetrieveUpdateDestroyAPIView):
    model = Subscription
    serializer_class = SubscriptionSerializer

    def destroy(self, request, *args, **kwargs):
        obj = super(SubscriptionDetail, self).get_object()

        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            raise ValidationError({"detail": "Failed to connect to Github account for Galaxy user %s. You must first authenticate with Github." % 
                request.user.username })

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except GithubException as e:
            raise ValidationError({"detail": "Failed to connect to Github API. This is most likely a temporary error, please try again in a few minutes. %s - %s" % 
                (e.data, e.status)})
    
        try:
            gh_repo = gh_api.get_repo(obj.github_user + '/' + obj.github_repo)
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to return repo for %s/%s." % 
                (obj.github_user, obj.github_repo, e.data, e.status)})
        
        try:
            gh_user = gh_api.get_user()
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to return authorized user. %s - %s" % 
                (e.data, e.status)})

        try:
            gh_user.remove_from_subscriptions(gh_repo)
        except GithubException as e:
            raise ValidationError({"detail": "GitHub API failed to unsubscribe %s from %s/%s. %s - %s" %
                (request.user.github_user, obj.github_user, obj.github_repo, e.data, e.status)})
        
        obj.delete()

        sub_count = 0
        for sub in gh_repo.get_subscribers():
            sub_count += 1   # only way to get subscriber count via pygithub
        
        for role in Role.objects.filter(github_user=obj.github_user,github_repo=obj.github_repo):
            role.watchers_count = sub_count
            role.save()
        
        return Response({ "detail": "unsubscribed %s from %s/%s." % 
            (request.user.github_user, obj.github_user, obj.github_repo)}, status=status.HTTP_202_ACCEPTED)

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
            raise ValidationError({ "detail": "Invalid request. Missing one or more required values." })

        if not source in ['github', 'travis']:
            raise ValidationError({ "detail": "Invalid source value. Expecting one of: [github, travis]"})
        
        if source == 'travis':
            secret = sha256(github_user + '/' + github_repo + secret).hexdigest()

        secret, create = NotificationSecret.objects.get_or_create(source=source, github_user=github_user, github_repo=github_repo,
            defaults = {
                'owner':  request.user,
                'source': source,
                'secret': secret,
                'github_user': github_user,
                'github_repo': github_repo
            }
        )

        if not create:
            raise ValidationError({ "detail": "Duplicate key. An integration for %s %s %s already exists." %
                (source, github_user, github_repo)})

        serializer = self.get_serializer(instance=secret)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class NotificationSecretDetail(RetrieveUpdateDestroyAPIView):
    model = NotificationSecret
    serializer_class = NotificationSecretSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, ModelAccessPermission,)

    def put(self, request, *args, **kwargs):
        source = request.data.get('source',None)
        secret = request.data.get('secret',None)
        github_user = request.data.get('github_user', None)
        github_repo = request.data.get('github_repo', None)
        
        if not secret or not source or not github_user or not github_repo:
            raise ValidationError({ "detail": "Invalid request. Missing one or more required values." })

        if not source in ['github', 'travis']:
            raise ValidationError({ "detail": "Invalid source value. Expecting one of: [github, travis]"})
        
        instance = self.get_object()

        try:
            instance.source = source
            instance.secret = secret
            instance.github_user = github_user
            instance.github_repo = github_repo
            instance.save()
        except IntegrityError as e:
            raise ValidationError({ "detail": "An integration for %s %s %s already exists." %
                (source, github_user, github_repo)})

        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, *args, **kwargs):
        obj = super(NotificationSecretDetail, self).get_object()
        obj.delete()
        return Response({ "detail": "Requested secret deleted. "}, status=status.HTTP_202_ACCEPTED)

class NotificationList(ListCreateAPIView):
    model = Notification
    serializer_class = NotificationSerializer

    def post(self, request, *args, **kwargs):
        if request.META.get('HTTP_TRAVIS_REPO_SLUG', None) or request.META.get('Travis-Repo-Slug', None):
            # travis
            secret = None
            if request.META.get('HTTP_AUTHORIZATION', None):
                secret = request.META['HTTP_AUTHORIZATION']
            if request.META.get('Authorization', None):
                secret = request.META['Authorization']
            
            if not secret:
                raise ValidationError('Invalid Request. Expected Authorization header.')
            
            try:
                ns = NotificationSecret.objects.get(secret=secret,active=True)
            except:
                raise ValidationError("Travis secret *****%s not found." % secret[-4:])

            repo = None
            if request.META.get('HTTP_TRAVIS_REPO_SLUG', None):
                repo = request.META['HTTP_TRAVIS_REPO_SLUG']
            if request.META.get('Travis-Repo-Slug'):
                repo = request.META['Travis-Repo-Slug']

            if not repo or repo != ns.repo_full_name():
                raise ValidationError('Invalid Request. Expected %s to match %s' % (repo, ns.repo_full_name()))
            
            payload = json.loads(request.data['payload'])
            request_branch = payload['branch']
            travis_status_url = "https://travis-ci.org/%s/%s.svg?branch=%s" % (ns.github_user,ns.github_repo,request_branch)
            
            notification = Notification.objects.create(
                owner = ns.owner,
                source = 'travis',
                github_branch = request_branch,
                travis_build_url = payload['build_url'],
                commit_message = payload['message'],
                committed_at = parse_datetime(payload['committed_at']),
                commit = payload['commit']
            )

            if Role.objects.filter(github_user=ns.github_user,github_repo=ns.github_repo,active=True).count() > 1:
                # multiple roles associated with github_user/github_repo
                for role in Role.objects.filter(github_user=ns.github_user,github_repo=ns.github_repo,active=True):    
                    notification.roles.add(role)
                    if role.github_branch and role.github_branch != request_branch:
                        notification.messages.append('Skipping role %d - github_branch %s does not match requested branch.' %
                            (role.id, role.github_branch))
                    else:
                        role.travis_status_url = travis_status_url
                        role.save()
                        task = create_import_task(role.github_user, role.github_repo, request_branch, role, ns.owner)
                        notification.imports.add(task)
            else:
                role, created = Role.objects.get_or_create(github_user=ns.github_user,github_repo=ns.github_repo, active=True,
                    defaults={
                        'namespace':   ns.github_user,
                        'name':        ns.github_repo,
                        'github_user': ns.github_user,
                        'github_repo': ns.github_repo,
                        'travis_status_url': travis_status_url,
                        'is_valid':    False,
                    }
                )
                notification.roles.add(role)
                if not created and role.github_branch and role.github_branch != request_branch:
                    notification.messages.append('Skipping role %d - github_branch %s does not match requested branch.' %
                    (role.id, role.github_branch))
                else:
                    if not created:
                        role.travis_status_url = travis_status_url
                        role.save()
                    task = create_import_task(role.github_user, role.github_repo, request_branch, role, ns.owner)
                    notification.imports.add(task)

            notification.save()
            serializer = self.get_serializer(instance=notification)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        ValidationError("Invalid request. Expecting Travis or GitHub web hook request.")


class NotificationDetail(RetrieveAPIView):
    model = Notification
    serializer_class = NotificationSerializer

class NotificationRolesList(SubListAPIView):
    model = Role
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
        can_change = check_user_access(request.user, User, 'change', obj, request.DATA)
        can_admin = check_user_access(request.user, User, 'admin', obj, request.DATA)
        if can_change and not can_admin:
            admin_only_edit_fields = ('full_name', 'username', 'is_active', 'is_superuser')
            changed = {}
            for field in admin_only_edit_fields:
                left = getattr(obj, field, None)
                right = request.DATA.get(field, None)
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
        return annotate_user_queryset(filter_user_queryset(qs))

class TopContributorsList(ListAPIView):
    model = Role
    serializer_class = TopContributorsSerializer

    def list(self, request, *args, **kwargs):
        qs = Role.objects.values('github_user').annotate(count=Count('id')).order_by('-count','github_user')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
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

class RoleSearchView(HaystackViewSet):
    index_models = [Role]
    serializer_class = RoleSearchSerializer
    url_path = ''
    lookup_sep = ','
    filter_backends = [HaystackFilter]

class FacetedView(APIView):
    def get(self, request, *agrs, **kwargs):
        facet_key = kwargs.get('facet_key')
        fkwargs = {}
        models = [apps.get_model(app_label='main', model_name=kwargs.get('model'))]
        qs = SearchQuerySet().models(*models)
        order = 'count'
        size = 20
        for key, value in request.GET.items():
            if key  == 'order':
                order = value
            if key == 'size':
                size = value
        if size:
            fkwargs['size'] = size
        if order:
            fkwargs['order'] = order
        qs = qs.facet(facet_key, **fkwargs)
        return Response(qs.facet_counts())

class UserSearchView(APIView):
    def get(self, request, *args, **kwargs):
        q = None
        page = 0
        page_size = 10
        order_fields = []
        for key,value in request.GET.items():
            if key in ('username','content','autocomplete'):
                q = Q('match', username=value)
            if key == 'page':
                page = int(value) - 1 if int(value) > 0 else 0
            if key == 'page_size':
                page_size = int(value)
            if key in ('order','order_by'):
                order_fields = value.split(',')
        s = Search(index='galaxy_users')
        s = s.query(q) if q else s
        s = s.sort(*order_fields) if len(order_fields) > 0 else s
        print ('get from: %d to %d' % (page * page_size, page * page_size + page_size))
        s = s[page * page_size:page * page_size + page_size]
        result = s.execute()
        serializer = ElasticSearchDSLSerializer(result.hits, many=True)
        response = get_response(request=request, result=result, view='api:user_search_view')
        response['results'] = serializer.data
        return Response(response)


class PlatformsSearchView(APIView):
    def get(self, request, *args, **kwargs):
        q = None
        page = 0
        page_size = 10
        order_fields = []
        for key,value in request.GET.items():
            if key == 'name':
                q = Q('match', name=value)
            if key == 'releases':
                q = Q('match', releases=value)
            if key in ('content','autocomplete'):
                q = Q('match', autocomplete=value)
            if key == 'page':
                page = int(value) - 1 if int(value) > 0 else 0
            if key == 'page_size':
                page_size = int(value)
            if key in ('order','order_by'):
                order_fields = value.split(',')
        s = Search(index='galaxy_platforms')
        s = s.query(q) if q else s
        s = s.sort(*order_fields) if len(order_fields) > 0 else s
        s = s[page * page_size:page * page_size + page_size]
        result = s.execute()
        serializer = ElasticSearchDSLSerializer(result.hits, many=True)
        response = get_response(request=request, result=result, view='api:platforms_search_view')
        response['results'] = serializer.data
        return Response(response)

class TagsSearchView(APIView):
    def get(self, request, *args, **kwargs):
        q = None
        page = 0
        page_size = 10
        order_fields = []
        for key,value in request.GET.items():
            if key in ('tag','content','autocomplete'):
                q = Q('match', tag=value)
            if key == 'page':
                page = int(value) - 1 if int(value) > 0 else 0
            if key == 'page_size':
                page_size = int(value)
            if key in ('order', 'orderby'):
                order_fields = value.split(',')
        s = Search(index='galaxy_tags')
        s = s.query(q) if q else s
        s = s.sort(*order_fields) if len(order_fields) > 0 else s
        s = s[page * page_size:page * page_size + page_size]
        result = s.execute()
        serializer = ElasticSearchDSLSerializer(result.hits, many=True)
        response = get_response(request=request, result=result, view='api:tags_search_view')
        response['results'] = serializer.data
        return Response(response)

class RemoveRole(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):

        gh_user = request.data.get('github_user', None)
        gh_repo = request.data.get('github_repo', None)
        
        if not gh_user or not gh_repo:
            raise ValidationError({ "detail": "Invalid request." })

        # Verify via GitHub API that user has access to requested role
        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            raise ValidationError({"detail": "Failed to get Github account for Galaxy user %s. You must first " +
                "authenticate with Github." % request.user.username })

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except:
            raise ValidationError({"detail": "Failed to connect to Github API. This is most likely a temporary " +
                "error, please try again in a few minutes."})
    
        try:
            ghu = gh_api.get_user()
        except:
            raise ValidationError({"detail": "Failed to get Github authorized user."})

        allowed = False
        repo_full_name = "%s/%s" % (gh_user, gh_repo)
        for r in ghu.get_repos():
            if r.full_name == repo_full_name:
                allowed = True
                continue
        if not allowed:
            raise ValidationError({"detail": "Galaxy user %s does not have access to repo %s" % (request.user.username,repo_full_name)})

        # User has access. Delete requested role and associated bits.
        response = OrderedDict([
            ('deleted_roles', []),
            ('status','')
        ])
        
        roles = Role.objects.filter(github_user=gh_user,github_repo=gh_repo)
        cnt = len(roles)
        if cnt == 0: 
            response['status'] = "Role %s.%s not found. Maybe it was deleted previously?" % (gh_user,gh_repo)
            return Response(response)
        elif cnt == 1:
            response['status'] = "Role %s.%s deleted" % (gh_user,gh_repo)
        else:
            response['status'] = "Deleted %d roles associated with %s/%s" % (len(roles),gh_user,gh_repo)

        for role in roles:
            response['deleted_roles'].append({
                "id": role.id,
                "namespace": role.namespace,
                "name": role.name,
                "github_user": role.github_user,
                "github_repo": role.github_repo
            })
            for notification in role.notifications.all():
                notification.delete()
                
        # Update the repository cache
        for repo in Repository.objects.filter(github_user=gh_user,github_repo=gh_repo):
            repo.is_enabled = False
            repo.save()

        Role.objects.filter(github_user=gh_user,github_repo=gh_repo).delete()
        ImportTask.objects.filter(github_user=gh_user,github_repo=gh_repo).delete()

        return Response(response)

    def put(self, request, *args, **kwargs):
        return self.delete(request, args, kwargs)

class RepositoryList(ListAPIView):
    model = Repository
    serializer_class = RepositorySerializer

    def get_queryset(self):
        qs = super(RepositoryList, self).get_queryset()
        qs.select_related('owner')
        return qs

class RepositoryDetail(RetrieveAPIView):
    model = Repository
    serializer_class = RepositorySerializer


class RefreshUserRepos(APIView):
    '''
    Return user GitHub repos directly from GitHub. Use to refresh cache for the authenticated user.
    '''

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Return a the list of user's repositories diretly from GitHub
        try:
            token = SocialToken.objects.get(account__user=request.user, account__provider='github')
        except:
            raise ValidationError({"detail": "Failed to connect to Github account for Galaxy user %s. You must first " +
                "authenticate with Github." % request.user.username })

        try:
            gh_api = Github(token.token)
            gh_api.get_api_status()
        except:
            raise ValidationError({"detail": "Failed to connect to Github API. This is most likely a temporary " +
                "error, please try again in a few minutes."})
    
        try:
            ghu = gh_api.get_user()
        except:
            raise ValidationError({"detail": "Failed to get Github authorized user."})

        response = {}
        response['results'] = []
        for r in ghu.get_repos():
            try:
                # check if repo is a role
                meta = r.get_file_contents("meta/main.yml")
                name = r.full_name.split('/')
                cnt = Role.objects.filter(github_user=name[0],github_repo=name[1]).count()
                role = {
                    'github_user': name[0],
                    'github_repo': name[1],
                    'is_enabled': cnt > 0,
                    'summary_fields': {
                        'notification_secrets': [{
                            'id': g.id,
                            'github_user': g.github_user,
                            'github_repo': g.github_repo,
                            'source': g.source,
                            'secret': '******' + g.secret[-4:]
                        } for g in NotificationSecret.objects.filter(github_user=name[0],github_repo=name[1])]
                    }
                }
                response['results'].append(role)
            except:
                pass
        
        # update the database    
        manage_user_repos.delay(request.user)
        
        return Response(response, status=status.HTTP_200_OK)


class TokenView(APIView):
    '''
    Allows ansible-galaxy CLI to retrieve an auth token
    '''
    def post(self, request, *args, **kwargs):
        
        gh_user = None
        user = None
        token = None
        github_token = request.data.get('github_token', None)
        
        if github_token == None:
            raise ValidationError({ "detail": "Invalid request." })
        
        try:
            git_status = requests.get('https://api.github.com')
            git_status.raise_for_status()
        except:
            raise ValidationError({"detail": "Error accessing Github API. Please try again later."})
        
        try:
            header = { 'Authorization': 'token ' + github_token }
            gh_user = requests.get('https://api.github.com/user', headers=header)
            gh_user.raise_for_status()
            gh_user = gh_user.json()
            if hasattr(gh_user,'message'):
                raise ValidationError({ "detail": gh_user['message'] })
        except:
            raise ValidationError({ "detail": "Error accessing Github with provided token." })
            
        if SocialAccount.objects.filter(provider='github',uid=gh_user['id']).count() > 0:
            user = SocialAccount.objects.get(provider='github',uid=gh_user['id']).user
        else:
            raise ValidationError({ "detail": "Galaxy user not found. You must first log into Galaxy using your Github account."})
        
        if Token.objects.filter(user=user).count() > 0:
            token = Token.objects.filter(user=user)[0]
        else:
            token = Token.objects.create(user=user)
            token.save()
        return Response({ "token": token.key, "username": user.username }, status=status.HTTP_200_OK)

            
def get_response(*args, **kwargs):
    """ 
    Create a response object with paging, count and timing attributes for search result views.
    """
    page = 0
    page_size = 10
    num_pages = 1
    cur_page = 1
    response = OrderedDict()

    request = kwargs.pop('request', None)
    result = kwargs.pop('result', None)
    view = kwargs.pop('view', None)
    
    for key, value in request.GET.items():
        if key == 'page':
            page = int(value) - 1 if int(value) > 0 else 0
        if key == 'page_size':
            page_size = int(value)
    
    if result:
        num_pages = int(math.ceil(result.hits.total / float(page_size)))
        cur_page = page + 1
        response['cur_page'] = cur_page
        response['num_pages'] = num_pages
        response['page_size'] = page_size
    
        if view:
            if num_pages > 1 and cur_page < num_pages:
                response['next_page'] = "%s?&page=%s" % (reverse(view), page + 2)
            if num_pages > 1 and cur_page > 1:
                response['prev_page'] = "%s?&page=%s" % (reverse(view), cur_page - 1)   
            
        response['count'] = result.hits.total
        response['respose_time'] = result.took
        response['success'] = result.success()
    
    return response

#------------------------------------------------------------------------

# Create view functions for all of the class-based views to simplify inclusion
# in URL patterns and reverse URL lookups, converting CamelCase names to
# lowercase_with_underscore (e.g. MyView.as_view() becomes my_view).
this_module = sys.modules[__name__]
for attr, value in locals().items():
    if isinstance(value, type) and issubclass(value, APIView):
        name = camelcase_to_underscore(attr)
        view = value.as_view()
        setattr(this_module, name, view)
