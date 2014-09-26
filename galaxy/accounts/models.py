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

from __future__ import unicode_literals
import re

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        UserManager)
from django.core.mail import send_mail
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from galaxy.api.aggregators import *
from galaxy.main.mixins import *

class CustomUser(AbstractBaseUser, PermissionsMixin, DirtyMixin):
    """
    A custom user class that basically mirrors Django's `AbstractUser` class
    and doesn't force `first_name` or `last_name` with sensibilities for
    international names.

    http://www.w3.org/International/questions/qa-personal-names
    """
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ])
    full_name = models.CharField(_('full name'), max_length=254, blank=True)
    short_name = models.CharField(_('short name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True, db_index=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # custom fields
    karma = models.IntegerField(default = 0, db_index = True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
        return self.username

    def mark_inactive(self, save=True):
        '''Use instead of delete to rename and mark inactive.'''

        if self.is_active:
            if 'username' in self._meta.get_all_field_names():
                self.name   = "_deleted_%s_%s" % (timezone.now().isoformat(), self.username)
            self.is_active = False
            if save:
                self.save()

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

    def get_num_ratings(self):
        return self.ratings.filter(active=True, role__active=True, role__is_valid=True).count()

    def get_rating_average(self):
        return self.ratings.filter(active=True, role__active=True, role__is_valid=True).aggregate(
                   avg_rating = AvgWithZeroForNull('score'),
               )['avg_rating']

    def get_num_roles(self):
        return self.roles.filter(active=True, is_valid=True).count()

    def get_role_average(self):
        return self.roles.filter(active=True, is_valid=True).aggregate(
                   avg_score = AvgWithZeroForNull('ratings__score'),
               )['avg_score']

    def get_role_aw_average(self):
        return self.roles.filter(ratings__owner__is_staff=True, active=True, is_valid=True).aggregate(
                   avg_score = AvgWithZeroForNull('ratings__score'),
               )['avg_score']

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def hasattr(self, attr):
        return hasattr(self, attr)
