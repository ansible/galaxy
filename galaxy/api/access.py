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

# standard python libraries

import logging

from allauth.account.models import EmailAddress, EmailConfirmation
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from galaxy.main import models
from django.core import exceptions

__all__ = ['check_user_access']

User = get_user_model()
logger = logging.getLogger('galaxy.api.access')

access_registry = {
    # <model_class>: [<access_class>, ...],
    # ...
}


def register_access(model_class, access_class):
    access_classes = access_registry.setdefault(model_class, [])
    access_classes.append(access_class)


def check_user_access(user, model_class, action, *args, **kwargs):
    """
    Return True if user can perform action against model_class with the
    provided parameters.
    """
    for access_class in access_registry.get(model_class, []):
        access_instance = access_class(user)
        access_method = getattr(access_instance, 'can_%s' % action, None)
        if not access_method:
            continue
        result = access_method(*args, **kwargs)
        logger.debug('%s.%s %r returned %r',
                     access_instance.__class__.__name__,
                     access_method.__name__, args, result)
        if result:
            return result
    return False


def get_pk_from_dict(_dict, key):
    """
    Helper for obtaining a pk from user data dict or None if not present.
    """
    try:
        return int(_dict[key])
    except (TypeError, KeyError, ValueError):
        return None


class BaseAccess(object):
    """
    Base class for checking user access to a given model.  Subclasses should
    define the model attribute, override the get_queryset method to return only
    the instances the user should be able to view, and override/define can_*
    methods to verify a user's permission to perform a particular action.
    """

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
            return bool(self.can_change(obj, None) and check_user_access(
                self.user, type(sub_obj), 'read', sub_obj))

    def can_unattach(self, obj, sub_obj, relationship):
        return self.can_change(obj, None)


class UserAccess(BaseAccess):
    """
    I can see user records when:
     - always
    I can change some fields for a user (mainly password) when I am that user.
    I can change all fields for a user (admin access) or delete when:
     - I'm an admin/staff
    """

    model = User

    def get_queryset(self):
        return self.model.objects.filter(
            is_active=True, is_admin=False).distinct()

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
    model = models.Content

    def can_attach(self, obj, sub_obj, relationship, data,
                   skip_sub_obj_read_check=False):
        return False

    def get_queryset(self):
        return self.model.objects.filter(active=True).distinct()


class RepositoryVersionAccess(BaseAccess):
    model = models.RepositoryVersion

    def get_queryset(self):
        return self.model.objects.filter(
            active=True, role__active=True).distinct()


class NotificationSecretAccess(BaseAccess):
    model = models.NotificationSecret

    def can_read(self, obj):
        if (self.user.is_authenticated() and obj.active
                and obj.owner.id == self.user.id):
            return True
        return False

    def can_add(self, data):
        return self.user.is_authenticated()

    def can_change(self, obj, data):
        if (self.user.is_authenticated() and obj.active
                and obj.owner.id == self.user.id):
            return True
        return False

    def can_delete(self, obj):
        if (self.user.is_authenticated() and obj.active
                and obj.owner.id == self.user.id):
            return True


class ImportTaskAccess(BaseAccess):
    model = models.ImportTask

    def can_add(self, data):
        return self.user.is_authenticated()

    def can_change(self, obj, data):
        return False

    def can_attach(self, obj, sub_obj, relationship, data,
                   skip_sub_obj_read_check=False):
        return False


class ImportTaskMessageAccess(BaseAccess):
    model = models.ImportTaskMessage

    def can_add(self, data):
        return False

    def can_change(self, obj, data):
        return False

    def can_attach(self, obj, sub_obj, relationship, data,
                   skip_sub_obj_read_check=False):
        return False

    def get_queryset(self):
        return self.model.objects.filter(
            active=True, task__active=True).distinct()


class NotificationAccess(BaseAccess):

    def can_add(self, data):
        return True

    def can_change(self, obj, data):
        return False

    def can_attach(self, obj, sub_obj, relationship, data,
                   skip_sub_obj_read_check=False):
        return False


class SubscriptionAccess(BaseAccess):
    def can_add(self, data):
        return self.user.is_authenticated()

    def can_change(self, obj, data):
        return False

    def can_delete(self, obj):
        return self.user.is_authenticated()


class StargazerAccess(BaseAccess):
    def can_add(self, data):
        return self.user.is_authenticated()

    def can_change(self, obj, data):
        return False

    def can_delete(self, obj):
        return self.user.is_authenticated()


class NamespaceAccess(BaseAccess):
    def can_read(self, obj):
        return True

    def can_add(self, data):
        return self.user.is_authenticated() and self.user.is_staff

    def can_change(self, obj, data):
        return self.user.is_authenticated()

    def can_delete(self, obj):
        return self.user.is_authenticated() and self.user.is_staff


class ProviderNamespaceAccess(BaseAccess):
    def can_read(self, obj):
        return True

    def can_add(self, data):
        return self.user.is_authenticated()

    def can_change(self, obj, data):
        return self.user.is_authenticated()

    def can_delete(self, obj):
        return self.user.is_authenticated()


class RepositoryAccess(BaseAccess):
    def can_read(self, obj):
        return True

    def can_add(self, data):
        return self.user.is_authenticated()

    def can_change(self, obj, data):
        return self.user.is_authenticated()

    def can_delete(self, obj):
        return self.user.is_authenticated()


class ContentBlockAccess(BaseAccess):
    def can_read(self, obj):
        return True


class ContentTypeAccess(BaseAccess):
    def can_read(self, obj):
        return True


class CloudPlatformsAccess(BaseAccess):
    def can_read(self, obj):
        return True


class UserTokenAccess(BaseAccess):
    model = Token

    def can_read(self, obj):
        if not self.user.is_authenticated():
            return False
        if self.user.is_staff or self.user.pk == obj.user.pk:
            return True
        return False

    def can_add(self):
        return False

    def can_change(self, obj, data):
        return self.can_read(obj)

    def can_delete(self, obj):
        return False


class CommunitySurveyAccess(BaseAccess):
    def can_read(self, obj):
        return True

    def can_add(self, data):
        return self.user.is_authenticated()

    def can_change(self, obj, data):
        return self.user == obj.user

    def can_delete(self, data):
        return False


class EmailAddressAccess(BaseAccess):
    model = EmailAddress

    def can_read(self, obj):
        if self.user.is_authenticated():
            if self.user.is_staff:
                return True
            if self.user == obj.user:
                return True
        return False

    def can_add(self, data):
        if self.user.is_authenticated():
            if self.user.id == data.get('user'):
                return True
        return False

    def can_change(self, obj, data):
        if self.user.is_authenticated():
            if self.user == obj.user:
                return True
        return False

    def can_delete(self, obj):
        if self.user.is_authenticated():
            if self.user.is_staff:
                return True
            if self.user == obj.user:
                return True
        return False


class EmailConfirmationAccess(BaseAccess):
    # Emails are verified via GET request. This means that emails can be
    # verified without requiring authentication if a confirmation key exists.
    def can_read(self, obj):
        return True

    def can_add(self, data):
        if self.user.is_authenticated():
            if data.get('email_address') is None:
                return False

            try:
                email = EmailAddress.objects.get(pk=data.get('email_address'))
            except exceptions.ObjectDoesNotExist:
                return False

            return email.user == self.user

        return False

    def can_change(self, obj, data):
        return False

    def can_delete(self, data):
        return False


class InfluxSessionAccess(BaseAccess):
    model = models.InfluxSessionIdentifier

    def can_read(self, obj):
        return True

    def can_add(self, data):
        return True

    def can_change(self, obj, data):
        return False

    def can_delete(self, obj):
        return False


class UserPreferencesAccess(BaseAccess):
    model = models.UserPreferences

    def can_add(self, data):
        return False

    def can_change(self, obj, data):
        if not self.user.is_authenticated:
            return False
        return bool(self.user == obj.user)

    def can_read(self, obj):
        if not self.user.is_authenticated:
            return False
        return bool(self.user == obj.user)

    def can_delete(self, obj):
        return False


register_access(EmailConfirmation, EmailConfirmationAccess)
register_access(User, UserAccess)
register_access(EmailAddress, EmailAddressAccess)
register_access(Token, UserTokenAccess)

register_access(models.Content, RoleAccess)
register_access(models.RepositoryVersion, RepositoryVersionAccess)
register_access(models.ImportTask, ImportTaskAccess)
register_access(models.ImportTaskMessage, ImportTaskMessageAccess)
register_access(models.NotificationSecret, NotificationSecretAccess)
register_access(models.Notification, NotificationAccess)
register_access(models.Subscription, SubscriptionAccess)
register_access(models.Stargazer, StargazerAccess)
register_access(models.Namespace, NamespaceAccess)
register_access(models.ProviderNamespace,
                ProviderNamespaceAccess)
register_access(models.Repository, RepositoryAccess)
register_access(models.ContentBlock, ContentBlockAccess)
register_access(models.ContentType, ContentTypeAccess)
register_access(models.CloudPlatform, CloudPlatformsAccess)
register_access(models.CommunitySurvey, CommunitySurveyAccess)
register_access(models.InfluxSessionIdentifier, InfluxSessionAccess)
register_access(models.UserPreferences, UserPreferencesAccess)
