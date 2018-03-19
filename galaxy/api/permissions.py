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

# Python
import logging

# Django
from django.contrib.auth.models import AnonymousUser
from django.http import Http404

# Django REST Framework
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions

# galaxy
from .access import check_user_access
from .utils import get_object_or_400
from galaxy.main.models import Namespace

logger = logging.getLogger('galaxy.api.permissions')

__all__ = ['ModelAccessPermission']


class ModelAccessPermission(permissions.BasePermission):
    '''
    Default permissions class to check user access based on the model and
    request method, optionally verifying the request data.
    '''

    def check_options_permissions(self, request, view, obj=None):
        return self.check_get_permissions(request, view, obj)

    def check_head_permissions(self, request, view, obj=None):
        return self.check_get_permissions(request, view, obj)

    def check_get_permissions(self, request, view, obj=None):
        if hasattr(view, 'parent_model'):
            parent_obj = get_object_or_400(view.parent_model, pk=view.kwargs['pk'])
            if not check_user_access(request.user, view.parent_model, 'read',
                                     parent_obj):
                return False
        if not obj:
            return True
        return check_user_access(request.user, view.model, 'read', obj)

    def check_post_permissions(self, request, view, obj=None):
        if hasattr(view, 'parent_model'):
            get_object_or_400(view.parent_model, pk=view.kwargs['pk'])
            return True
        else:
            if obj:
                return True
            if hasattr(view, 'model'):
                return check_user_access(request.user, view.model, 'add', request.data)
            return True

    def check_put_permissions(self, request, view, obj=None):
        if not obj:
            # FIXME: For some reason this needs to return True
            # because it is first called with obj=None?
            return True

        if getattr(view, 'is_variable_data', False):
            return check_user_access(request.user, view.model, 'change', obj,
                                     dict(variables=request.data))
        else:
            return check_user_access(request.user, view.model, 'change', obj,
                                     request.data)

    def check_patch_permissions(self, request, view, obj=None):
        return self.check_put_permissions(request, view, obj)

    def check_delete_permissions(self, request, view, obj=None):
        if not obj:
            # FIXME: For some reason this needs to return True
            # because it is first called with obj=None?
            return True
        return check_user_access(request.user, view.model, 'delete', obj)

    def check_permissions(self, request, view, obj=None):
        '''
        Perform basic permissions checking before delegating to the appropriate
        method based on the request method.
        '''

        # Check that obj (if given) is active, otherwise raise a 404.
        active = getattr(obj, 'active', getattr(obj, 'is_active', True))
        if callable(active):
            active = active()
        if not active and not isinstance(obj, AnonymousUser) and not isinstance(obj, Namespace):
            raise Http404()

        # Don't allow inactive users (and respond with a 403).
        # Anonymous users never show up as active, so we skip them here,
        # they'll be checked for other permissions later.
        if not request.user.is_active and not request.user.is_anonymous:
            raise PermissionDenied('your account is inactive')

        # Always allow superusers (as long as they are active).
        if request.user.is_staff:
            return True

        # Check permissions for the given view and object, based on the request
        # method used.
        check_method = getattr(self, 'check_%s_permissions' % request.method.lower(), None)
        result = check_method and check_method(request, view, obj)
        if not result:
            raise PermissionDenied("You do not have permission to perform this action.")
        return result

    def has_permission(self, request, view, obj=None):
        # logger.debug('has_permission(user=%s method=%s data=%r, %s, %r)',
        #             request.user, request.method, request.data,
        #             view.__class__.__name__, obj)
        try:
            response = self.check_permissions(request, view, obj)
        except Exception as e:
            logger.debug('has_permission raised %r', e, exc_info=True)
            raise
        else:
            logger.debug('has_permission returned %r', response)
            return response

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view, obj)
