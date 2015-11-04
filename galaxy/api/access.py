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
import logging

# django stuff

from django.contrib.auth import get_user_model
from django.db.models import Count

# rest framework stuff

from rest_framework.exceptions import ParseError, PermissionDenied

# local stuff

from galaxy.accounts.models import CustomUser
from galaxy.main.models import *

logger = logging.getLogger('galaxy.api.access')

__all__ = ['check_user_access']

User = get_user_model()

access_registry = {
    # <model_class>: [<access_class>, ...],
    # ...
}

def register_access(model_class, access_class):
    access_classes = access_registry.setdefault(model_class, [])
    access_classes.append(access_class)

def check_user_access(user, model_class, action, *args, **kwargs):
    '''
    Return True if user can perform action against model_class with the
    provided parameters.
    '''
    for access_class in access_registry.get(model_class, []):
        access_instance = access_class(user)
        access_method = getattr(access_instance, 'can_%s' % action, None)
        if not access_method:
            continue
        result = access_method(*args, **kwargs)
        logger.debug('%s.%s %r returned %r', access_instance.__class__.__name__,
                     access_method.__name__, args, result)
        if result:
            return result
    logger.debug('check_user_access: %s %s %s returned %s', user, model_class, action, False)
    return False

def get_pk_from_dict(_dict, key):
    '''
    Helper for obtaining a pk from user data dict or None if not present.
    '''
    try:
        return int(_dict[key])
    except (TypeError, KeyError, ValueError):
        return None

class BaseAccess(object):
    '''
    Base class for checking user access to a given model.  Subclasses should
    define the model attribute, override the get_queryset method to return only
    the instances the user should be able to view, and override/define can_*
    methods to verify a user's permission to perform a particular action.
    '''

    model = None

    def __init__(self, user):
        self.user = user

    def get_queryset(self):
        return self.model.objects.filter(active=True).distinct()

    def can_read(self, obj):
        if obj:
            if hasattr(obj, "active") and obj.active:
                if hasattr(obj, "is_valid") and not obj.is_valid:
                    return False
                return True
            elif hasattr(obj, "is_active") and obj.is_active:
                return True
            else:
                return False
        return True

    def can_add(self, data):
        return self.user.is_staff

    def can_change(self, obj, data):
        if hasattr(obj, 'owner_id'):
            return obj.owner == self.user or self.user.is_staff
        return self.user.is_staff

    def can_write(self, obj, data):
        # Alias for change.
        return self.can_change(obj, data)

    def can_admin(self, obj, data):
        # Alias for can_change.  Can be overridden if admin vs. user change
        # permissions need to be different.
        return self.can_change(obj, data)

    def can_delete(self, obj):
        return self.user.is_staff

    def can_attach(self, obj, sub_obj, relationship, data,
                   skip_sub_obj_read_check=False):
        if skip_sub_obj_read_check:
            return self.can_change(obj, None)
        else:
            return bool(self.can_change(obj, None) and
                        check_user_access(self.user, type(sub_obj), 'read', sub_obj))

    def can_unattach(self, obj, sub_obj, relationship):
        return self.can_change(obj, None)

class UserAccess(BaseAccess):
    '''
    I can see user records when:
     - always
    I can change some fields for a user (mainly password) when I am that user.
    I can change all fields for a user (admin access) or delete when:
     - I'm an admin/staff
    '''

    model = User

    def get_queryset(self):
        return self.model.objects.filter(is_active=True, is_admin=False).distinct()

    def can_change(self, obj, data):
        # A user can be changed if they are themselves, or by org admins or
        # superusers.  Change permission implies changing only certain fields
        # that a user should be able to edit for themselves.
        return bool(self.user == obj or self.user.is_staff)

    def can_delete(self, obj):
        if obj == self.user:
            # cannot delete yourself
            return False
        return self.user.is_staff

class RoleAccess(BaseAccess):
    model = Role

    def can_attach(self, obj, sub_obj, relationship, data,
                   skip_sub_obj_read_check=False):

        # unauthenticated users can never attach
        if not self.user.is_authenticated:
            return False
        
        if isinstance(sub_obj, RoleRating):
            if obj.owner.id == self.user.id:
                # people cannot rate their own roles
                return False
            else:
                # but everyone else can
                return True
        return False

    def get_queryset(self):
        qs = self.model.objects.filter(active=True, owner__is_active=True).distinct()

class RoleRatingAccess(BaseAccess):
    model = RoleRating

    def can_add(self, data):
        return self.user.is_authenticated

    def can_change(self, obj, data):
        if not self.user.is_authenticated:
            return False
        if not hasattr(obj, "owner"):
            return False
        return bool(obj.owner.id == self.user.id or self.user.is_staff)

    def get_queryset(self):
        qs = self.model.objects.filter(active=True, role__active=True, role__owner__is_active=True).distinct()

class RoleVersionAccess(BaseAccess):
    model = RoleVersion

    def get_queryset(self):
        qs = self.model.objects.filter(active=True, role__active=True, role__owner__is_active=True).distinct()

class RoleImportAccess(BaseAccess):
    model = RoleImport

    def get_queryset(self):
        qs = self.model.objects.filter(active=True, role__active=True, role__owner__is_active=True).distinct()

register_access(User, UserAccess)
register_access(Role, RoleAccess)
register_access(RoleRating, RoleRatingAccess)
register_access(RoleVersion, RoleVersionAccess)
register_access(RoleImport, RoleImportAccess)
