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

import galaxy.main.mixins as mixins


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
            validators.RegexValidator(re.compile(r'^[a-zA-Z0-9_.@+-]+$'),
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

    objects = auth_models.UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

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
