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

from django.core import exceptions
from django.core.mail import send_mail
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
            validators.RegexValidator(re.compile('^[\w.@+-]+$'),
                                      _('Enter a valid username.'),
                                      'invalid')
        ])
    full_name = models.CharField(_('full name'), max_length=254, blank=True)
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
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    karma = models.IntegerField(default=0, db_index=True)
    github_avatar = models.CharField(
        _('github avatar'), max_length=254, blank=True)
    github_user = models.CharField(
        _('github user'), max_length=254, blank=True)
    cache_refreshed = models.BooleanField(
        _('cache refreshed'), default=False)

    objects = auth_models.UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
        return self.username

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = self.full_name
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.short_name.strip()

    def get_num_roles(self):
        return self.roles.filter(active=True, is_valid=True).count()

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def hasattr(self, attr):
        return hasattr(self, attr)

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

    def get_subscriber(self, github_user, github_repo):
        try:
            return self.subscriptions.get(
                github_user=github_user,
                github_repo=github_repo)
        except exceptions.ObjectDoesNotExist:
            return None

    def get_stargazer(self, github_user, github_repo):
        try:
            star = self.starred.get(
                repository__provider_namespace__name=github_user,
                repository__name=github_repo)
            return star
        except exceptions.ObjectDoesNotExist:
            return None

    def is_connected_to_github(self):
        connected = False
        for account in self.socialaccount_set.all():
            if account.provider == 'github':
                connected = True
        return connected
