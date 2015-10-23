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

# standard python libs

import random

# django libs

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Avg
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils.timezone import now, make_aware, get_default_timezone

# postgresql specific
from django.contrib.postgres.fields import ArrayField

# celery/djcelery

from djcelery.models import TaskMeta

# local stuff

#from galaxy.api.access import *
from galaxy.api.aggregators import *
from galaxy.main.fields import *
from galaxy.main.mixins import *

__all__ = [
    'PrimordialModel', 'Platform', 'Category', 'Tag', 'Role', 'RoleRating', 'RoleImport', 'RoleVersion', 'UserAlias',
]

###################################################################################
# Our custom user class, brought in here so it can be used commonly throughout
# the rest of the codebase

#User = get_user_model()

###################################################################################
# Abstract models that form a base for all real models

class PrimordialModel(models.Model, DirtyMixin):
    '''
    common model for all object types that have these standard fields
    must use a subclass CommonModel or CommonModelNameNotUnique though
    as this lacks a name field.
    '''

    class Meta:
        abstract = True

    description   = TruncatingCharField(max_length=255, blank=True, default='')
    created       = models.DateTimeField(auto_now_add=True)
    modified      = models.DateTimeField(auto_now=True)
    active        = models.BooleanField(default=True, db_index=True)

    #tags = TaggableManager(blank=True)

    def __unicode__(self):
        if hasattr(self, 'name'):
            return unicode("%s-%s"% (self.name, self.id))
        else:
            return u'%s-%s' % (self._meta.verbose_name, self.id)

    def save(self, *args, **kwargs):
        # For compatibility with Django 1.4.x, attempt to handle any calls to
        # save that pass update_fields.
        try:
            super(PrimordialModel, self).save(*args, **kwargs)
        except TypeError:
            if 'update_fields' not in kwargs:
                raise
            kwargs.pop('update_fields')
            super(PrimordialModel, self).save(*args, **kwargs)

    def mark_inactive(self, save=True):
        '''Use instead of delete to rename and mark inactive.'''

        if self.active:
            if 'name' in self._meta.get_all_field_names():
                self.original_name = self.name
                self.name = "_deleted_%s_%s" % (now().isoformat(), self.name)
            self.active = False
            if save:
                self.save()

    def mark_active(self, save=True):
        '''
        If previously marked inactive, this function reverses the
        renaming and sets the active flag to true
        '''

        if not self.active:
            if self.original_name != "":
                self.name = self.original_name
                self.original_name = ""
            self.active = True
            if save:
                self.save()

    def hasattr(self, attr):
        return hasattr(self, attr)

class CommonModel(PrimordialModel):
    ''' a base model where the name is unique '''

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=True, db_index=True)
    original_name = models.CharField(max_length=512)

class CommonModelNameNotUnique(PrimordialModel):
    ''' a base model where the name is not unique '''

    class Meta:
        abstract = True

    name = models.CharField(max_length=512, unique=False, db_index=True)
    original_name = models.CharField(max_length=512)

###################################################################################
# Actual models

class Category(CommonModel):
    '''
    a class represnting the valid categories (formerly tags) that can be
    assigned to a role
    '''
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:category_detail', args=(self.pk,))

    #def get_num_roles(self):
    #    return self.roles.filter(active=True, owner__is_active=True).count()

class Tag(CommonModel):
    '''
    a class representing the tags that have been assigned to roles
    '''
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Tags'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:tag_detail', args=(self.pk,))

    def get_num_roles(self):
        return self.roles.filter(active=True, owner__is_active=True).count()


class Platform(CommonModelNameNotUnique):
    ''' a class represnting the valid platforms a role supports '''
    class Meta:
        ordering = ['name','release']

    release = models.CharField(
        max_length   = 50,
        verbose_name = "Distribution Release Version",
    )
    alias = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "Search terms"
    )

    def __unicode__(self):
        return "%s-%s" % (self.name, self.release)

    def get_absolute_url(self):
        return reverse('api:platform_detail', args=(self.pk,))

class UserAlias(models.Model):
    '''
    a class representing a mapping between users and aliases
    to allow for user renaming without breaking deps
    '''
    class Meta:
        verbose_name_plural = "UserAliases"

    alias_of = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'aliases',
    )
    alias_name = models.CharField(
        # must be in-sync with galaxy/accounts/models.py:CustomUser
        max_length   = 30,
        unique       = True,
    )

    def __unicode__(self):
        return unicode("%s (alias of %s)"% (self.alias_name, self.alias_of.username))

class Role(CommonModelNameNotUnique):
    ''' a class representing a user role '''

    class Meta:
        unique_together = ('owner','name')

    #------------------------------------------------------------------------------
    # foreign keys

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'roles',
        editable     = False,
    )
    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name = 'author_on',
        editable     = False,
    )
    dependencies = models.ManyToManyField(
        'Role',
        related_name = '+',
        blank        = True,
        editable     = False,
    )
    platforms = models.ManyToManyField(
        'Platform',
        related_name = 'roles',
        verbose_name = "Supported Platforms",
        blank        = True,
        editable     = False,
    )
    platforms.help_text = ""

    tags = models.ManyToManyField(
        'Tag',
        related_name = 'roles',
        verbose_name = 'Tags',
        blank        = True,
        editable     = False,    
    )
    tags.help_text = ""

    categories = models.ManyToManyField(
        'Category',
        related_name = 'categories',
        verbose_name = "Categories",
        blank        = True,
        editable     = False,    
    )
    categories.help_text = ""

    #------------------------------------------------------------------------------
    # regular fields

    github_user = models.CharField(
        max_length   = 256,
        verbose_name = "Github Username",
    )
    github_repo = models.CharField(
        max_length   = 256,
        verbose_name = "Github Repository",
    )
    readme = models.TextField(
        blank=True,
        default='',
    )
    min_ansible_version = models.CharField(
        max_length   = 10,
        blank        = True,
        null         = True,
        verbose_name = "Minimum Ansible Version Required",
    )
    issue_tracker_url = models.CharField(
        max_length   = 256,
        blank        = True,
        null         = True,
        verbose_name = "Issue Tracker URL",
    )
    license = models.CharField(
        max_length   = 30,
        blank        = True,
        verbose_name = "License (optional)",
    )
    company = models.CharField(
        max_length   = 50,
        blank        = True,
        null         = True,
        verbose_name = "Company Name (optional)",
    )
    is_valid = models.BooleanField(
        default      = False,
        editable     = True,
        db_index     = True,
    )
    featured = models.BooleanField(
        default      = False,
        editable     = False,
    )
    
    #tags = ArrayField(models.CharField(max_length=256), null=True, editable=True, size=100)

    #------------------------------------------------------------------------------
    # fields calculated by a celery task or signal, not set

    bayesian_score = models.FloatField(
        default    = 0.0,
        db_index   = True,
        editable   = False,
    )
    num_ratings = models.IntegerField(
        default    = 0,
        db_index   = False,
    )
    average_score = models.FloatField(
        default    = 0.0,
        db_index   = False,
    )
    
    #------------------------------------------------------------------------------
    # other functions and properties

    def __unicode__(self):
        return "%s.%s" % (self.owner.username,self.name)

    def get_last_import(self):
        try:
            return model_to_dict(self.imports.latest(), fields=('released','state','status_message'))
        except Exception, e:
            return {}

    def get_unique_platforms(self):
        return [platform.name for platform in self.platforms.filter(active=True).order_by('name').distinct('name')]

    def get_unique_platform_versions(self):
        return [platform.release for platform in self.platforms.filter(active=True).order_by('release').distinct('release')]
    
    def get_unique_platform_search_terms(self):
        '''
        Fetch the unique set of aliases
        '''
        terms = []
        for platform in self.platforms.filter(active=True).exclude(alias__isnull=True).exclude(alias__exact='').all():
            terms += platform.alias.split(' ')
        return set(terms)
    
    def get_username(self):
        return self.owner.username

    def get_tags(self):
        return [tag.name for tag in self.tags.filter(active=True)]
    
class RoleVersion(CommonModelNameNotUnique):
    class Meta:
        ordering = ('-loose_version',)

    #------------------------------------------------------------------------------
    # foreign keys

    role = models.ForeignKey(
        Role,
        related_name = 'versions',
    )

    #------------------------------------------------------------------------------
    # regular fields

    release_date = models.DateTimeField(
        blank      = True,
        null       = True,
    )
    loose_version = LooseVersionField(
        editable   = False,
        db_index   = True,
    )

    #------------------------------------------------------------------------------
    # other functions and properties

    def __unicode__(self):
        return "%s.%s-%s" % (self.role.owner.username,self.role.name,self.name)

    def save(self, *args, **kwargs):
        # the value of score is based on the
        # values in the other rating fields
        self.loose_version = self.name
        super(RoleVersion, self).save(*args, **kwargs)

class RoleImport(PrimordialModel):
    class Meta:
        get_latest_by = "released"

    #------------------------------------------------------------------------------
    # foreign keys

    role = models.ForeignKey(Role,
        related_name = 'imports',
    )

    #------------------------------------------------------------------------------
    # regular fields

    celery_task_id = models.CharField(
        max_length   = 100,
        blank        = True,
        default      = '',
        editable     = False,
        db_index     = True,
    )
    released = models.DateTimeField(
        editable     = True,
        auto_now_add = True,
    )
    state = models.CharField(
        max_length   = 20,
        blank        = True,
        default      = '',
        #editable     = False,
        db_index     = True,
    )
    status_message = models.CharField(
        max_length   = 512,
        blank        = True,
        default      = '',
        #editable     = False,
    )

    #------------------------------------------------------------------------------
    # other functions and properties

    def __unicode__(self):
        return "%s-%s" % (self.role.name,self.released.strftime("%Y%m%d-%H%M%S-%Z"))

    @property
    def celery_task(self):
        try:
            if self.celery_task_id:
                return TaskMeta.objects.get(task_id=self.celery_task_id)
        except TaskMeta.DoesNotExist:
            return None

class RoleRating(PrimordialModel):

    class Meta:
        unique_together = ('owner','role')

    #------------------------------------------------------------------------------
    # foreign keys

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = 'ratings',
    )
    role = models.ForeignKey(
        Role,
        related_name = 'ratings',
    )
    
    #------------------------------------------------------------------------------
    # regular fields

    comment = models.TextField(
        blank      = True,
        null       = True,
    )
    score = models.IntegerField(
        default      = 0,
        db_index     = True,
    )

    #------------------------------------------------------------------------------
    # other functions and properties

    def __unicode__(self):
        return "%s.%s -> %s" % (self.role.owner.username,self.role.name,self.score)

    def save(self, *args, **kwargs):
        def clamp_range(value):
            value = int(value)
            if value > 5:
                return 5
            elif value < 1:
                return 1
            else:
                return value
        
        self.score = clamp_range(self.score)
        
        if len(self.comment) > 5000:
            self.comment = self.comment[:5000]
        print 'saving!' 
        super(RoleRating, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.pk:
            return reverse('api:rating_detail', args=(self.pk,))
        else:
            return ""
