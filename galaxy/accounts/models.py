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

from __future__ import unicode_literals
import re

from django.contrib.auth import models as auth_models

from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlquote
from django.utils import timezone
import six

import galaxy.main.mixins as mixins


@six.python_2_unicode_compatible
class CustomUser(auth_models.AbstractBaseUser,
                 auth_models.PermissionsMixin,
                 mixins.DirtyMixin):
    """
    A custom user class that basically mirrors Django's `AbstractUser` class
    and doesn't force `first_name` or `last_name` with sensibilities for
    international names.

    http://www.w3.org/International/questions/qa-personal-names
    """
    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'),
                                      _('Enter a valid username.'),
                                      'invalid')
        ])
    full_name = models.CharField(_('full name'), max_length=254, blank=True)
    # FIXME: This field looks unused
    short_name = models.CharField(_('short name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into '
                    'this admin site.'))
    is_active = models.BooleanField(
        _('active'),
        default=True,
        db_index=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now)
    avatar_url = models.CharField(
        _('avatar URL'),
        max_length=256,
        blank=True)

    # User email notification settings
    notify_survey = models.BooleanField(
        default=False,
        help_text='Notify me when a user adds a survey for my content.')
    notify_import_fail = models.BooleanField(
        default=False,
        help_text='Notify me when an import fails.')
    notify_import_success = models.BooleanField(
        default=False,
        help_text='Notify me when an import succeeds.')
    notify_content_release = models.BooleanField(
        default=False,
        help_text=("Notify me when a new release is available for "
                   "content I'm following."))
    notify_author_release = models.BooleanField(
        default=False,
        help_text=("Notify me when an author I'm following "
                   "creates new content."))
    notify_galaxy_announce = models.BooleanField(
        default=False,
        help_text='Notify me when there is a Galaxy announcement')

    objects = auth_models.UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    repositories_followed = models.ManyToManyField(
        'main.Repository',
        editable=True,
        blank=True
    )

    namespaces_followed = models.ManyToManyField(
        'main.Namespace',
        editable=True,
        blank=True
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

    # FIXME: replace with django.urls.reverse(..)
    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    # FIXME: This method implementation is optional since Django 2.0
    def get_full_name(self):
        return self.full_name.strip()

    # FIXME: This method implementation is optional since Django 2.0
    def get_short_name(self):
        return self.short_name.strip()

    def get_subscriptions(self):
        return [{
            'id': g.id,
            'github_user': g.github_user,
            'github_repo': g.github_repo,
        } for g in self.subscriptions.all()]

    def get_starred(self):
        return [{
            'id': g.id,
            'github_user': g.repository.github_user,
            'github_repo': g.repository.github_repo,
        } for g in self.starred.select_related('repository').all()]
