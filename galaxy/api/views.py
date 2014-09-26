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

# rest framework stuff

from rest_framework import filters
from rest_framework import mixins
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

# django stuff

from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, Avg
from django.http import Http404
from django.utils.datastructures import SortedDict

# local stuff

from galaxy.api.aggregators import *
from galaxy.api.access import *
from galaxy.api.base_views import *
from galaxy.api.permissions import *
from galaxy.api.serializers import *
from galaxy.main.models import *
from galaxy.main.utils import camelcase_to_underscore


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
               num_roles = Count('roles', distinct=True),
               avg_rating = AvgWithZeroForNull('ratings__score'),
               avg_role_score = AvgWithZeroForNull('roles__ratings__score'),
           )

def annotate_role_queryset(qs):
    return qs.annotate(
               num_ratings = Count('ratings', distinct=True),
               average_score = AvgWithZeroForNull('ratings__score'),
           )

#--------------------------------------------------------------------------------

class ApiRootView(APIView):
    permission_classes = (AllowAny,)
    view_name = 'REST API'
    def get(self, request, format=None):
        ''' list supported API versions '''
        current = reverse('api:api_v1_root_view', args=[])
        data = dict(
            description = 'GALAXY REST API',
            current_version = current,
            available_versions = dict(
                v1 = current
            )
        )
        return Response(data)

class ApiV1RootView(APIView):
    permission_classes = (AllowAny,)
    view_name = 'Version 1'
    def get(self, request, format=None):
        ''' list top level resources '''
        data = SortedDict()
        data['me']         = reverse('api:user_me_list')
        data['categories'] = reverse('api:category_list')
        data['platforms']  = reverse('api:platform_list')
        data['ratings']    = reverse('api:rating_list')
        data['users']      = reverse('api:user_list')
        data['roles']      = reverse('api:role_list')
        return Response(data)

class CategoryList(ListAPIView):
    model = Category
    serializer_class = CategorySerializer
    paginate_by = None

    def get_queryset(self):
        return self.model.objects.filter(active=True).annotate(num_roles=Count('roles'))

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

class RoleImportsList(SubListAPIView):
    model = RoleImport
    serializer_class = RoleImportSerializer
    parent_model = Role
    relationship = 'imports'

class RoleImportDetail(RetrieveUpdateDestroyAPIView):
    model = RoleImport
    serializer_class = RoleImportSerializer

class RoleRatingsList(SubListCreateAPIView):
    model = RoleRating
    serializer_class = RoleRatingSerializer
    parent_model = Role
    parent_key = 'role'
    relationship = 'ratings'

class RoleAuthorsList(SubListCreateAPIView):
    model = User
    serializer_class = UserSerializer
    parent_model = Role
    relationship = 'authors'

    def get_queryset(self):
        qs = super(RoleAuthorsList, self).get_queryset()
        return annotate_user_queryset(filter_user_queryset(qs))

class RoleDependenciesList(SubListCreateAPIView):
    model = Role
    serializer_class = RoleSerializer
    parent_model = Role
    relationship = 'dependencies'

    def get_queryset(self):
        qs = super(RoleDependenciesList, self).get_queryset()
        return annotate_role_queryset(filter_role_queryset(qs))

class RoleUsersList(SubListAPIView):
    model = User
    serializer_class = UserSerializer
    parent_model = Role
    relationship = 'created_by'

    def get_queryset(self):
        qs = super(RoleUsersList, self).get_queryset()
        return annotate_user_queryset(filter_user_queryset(qs))

class RoleVersionsList(SubListCreateAPIView):
    model = RoleVersion
    serializer_class = RoleVersionSerializer
    parent_model = Role
    relationship = 'versions'

class RoleList(ListCreateAPIView):
    model = Role
    serializer_class = RoleSerializer

    def get_queryset(self):
        qs = super(RoleList, self).get_queryset()
        return annotate_role_queryset(filter_role_queryset(qs))

class RoleDetail(RetrieveUpdateDestroyAPIView):
    model = Role
    serializer_class = RoleSerializer

    def get_object(self, qs=None):
        obj = super(RoleDetail, self).get_object(qs)
        if not obj.is_valid or not obj.active:
            raise Http404()
        return obj

class UserRatingsList(SubListAPIView):
    model = RoleRating
    serializer_class = RoleRatingSerializer
    parent_model = User
    relationship = 'ratings'

class UserRolesList(SubListAPIView):
    model = Role
    serializer_class = RoleSerializer
    parent_model = User
    relationship = 'roles'

    def get_queryset(self):
        qs = super(UserRolesList, self).get_queryset()
        return annotate_role_queryset(filter_role_queryset(qs))

class UserDetail(RetrieveUpdateDestroyAPIView):
    model = User
    serializer_class = UserSerializer

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
        obj = super(UserDetail, self).get_object(qs)
        if not obj.is_active:
            raise Http404()
        return obj

class UserList(ListAPIView):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super(UserList, self).get_queryset()
        return annotate_user_queryset(filter_user_queryset(qs))

class RatingList(ListAPIView):
    model = RoleRating
    serializer_class = RoleRatingSerializer

    def get_queryset(self):
        qs = super(RatingList, self).get_queryset()
        return filter_rating_queryset(qs)

class RatingDetail(RetrieveUpdateDestroyAPIView):
    model = RoleRating
    serializer_class = RoleRatingSerializer

    def get_object(self, qs=None):
        obj = super(RatingDetail, self).get_object(qs)
        if not obj.active or not obj.role.active:
            raise Http404()
        return obj

class RatingUpVotesList(SubListCreateAPIView):
    model = User
    serializer_class = VoteSerializer
    parent_model = RoleRating
    relationship = 'up_votes'

    def get_queryset(self):
        qs = super(RatingUpVotesList, self).get_queryset()
        return annotate_user_queryset(qs)

class RatingDownVotesList(SubListCreateAPIView):
    model = User
    serializer_class = VoteSerializer
    parent_model = RoleRating
    relationship = 'down_votes'

    def get_queryset(self):
        qs = super(RatingDownVotesList, self).get_queryset()
        return annotate_user_queryset(qs)

class UserMeList(RetrieveAPIView):
    model = User
    serializer_class = MeSerializer
    view_name = 'Me'

    def get_object(self, qs=None):
        try:
            obj = self.model.objects.get(pk=self.request.user.pk)
        except:
            obj = AnonymousUser()
        return obj

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
