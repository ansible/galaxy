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
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Avg
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils.timezone import now, make_aware, get_default_timezone

# celery/djcelery

from djcelery.models import TaskMeta

# local stuff

#from galaxy.api.access import *
from galaxy.api.aggregators import *
from galaxy.main.fields import *
from galaxy.main.mixins import *

__all__ = [
    'PrimordialModel', 'User', 'Platform', 'Category', 'Role', 'RoleRating', 'RoleImport', 'RoleVersion',
]

###################################################################################
# Our custom user class, brought in here so it can be used commonly throughout
# the rest of the codebase

User = get_user_model()

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
    modified      = models.DateTimeField(auto_now=True, default=now)
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
        User,
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
        User,
        related_name = 'roles',
        editable     = False,
    )
    authors = models.ManyToManyField(
        User,
        related_name = 'author_on',
        editable     = False,
    )
    dependencies = models.ManyToManyField(
        'Role',
        related_name = '+',
        blank        = True,
        editable     = False,
    )
    categories = models.ManyToManyField(
        Category,
        related_name = 'roles',
        verbose_name = "Categories",
        blank        = True,
        editable     = False,
    )
    categories.help_text = ""
    platforms = models.ManyToManyField(
        'Platform',
        related_name = 'roles',
        verbose_name = "Supported Platforms",
        blank        = True,
        editable     = False,
    )
    platforms.help_text = ""

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

    #------------------------------------------------------------------------------
    # fields calculated by a celery task, not set

    bayesian_score = models.FloatField(
        default    = 0.0,
        db_index   = True,
        editable   = False,
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

    def get_num_ratings(self):
        return self.ratings.filter(active=True).count()

    def get_average_score(self):
        return self.ratings.filter(active=True).aggregate(avg=AvgWithZeroForNull('score'))['avg']

    def get_average_composite(self):
        return self.ratings.filter(active=True).aggregate(
                   avg_reliability   = AvgWithZeroForNull('reliability'),
                   avg_documentation = AvgWithZeroForNull('documentation'),
                   avg_code_quality  = AvgWithZeroForNull('code_quality'),
                   avg_wow_factor    = AvgWithZeroForNull('wow_factor'),
               )

    def get_num_aw_ratings(self):
        return self.ratings.filter(owner__is_staff=True, active=True).count()
        
    def get_average_aw_score(self):
        return self.ratings.filter(owner__is_staff=True, active=True).aggregate(avg=AvgWithZeroForNull('score'))['avg']

    def get_average_aw_composite(self):
        return self.ratings.filter(owner__is_staff=True, active=True).aggregate(
                   avg_reliability   = AvgWithZeroForNull('reliability'),
                   avg_documentation = AvgWithZeroForNull('documentation'),
                   avg_code_quality  = AvgWithZeroForNull('code_quality'),
                   avg_wow_factor    = AvgWithZeroForNull('wow_factor'),
               )

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
        User,
        related_name = 'ratings',
    )
    role = models.ForeignKey(
        Role,
        related_name = 'ratings',
    )
    up_votes = models.ManyToManyField(
        User,
        related_name = 'user_up_votes',
        null         = True,
        default      = None,
    )
    down_votes = models.ManyToManyField(
        User,
        related_name = 'user_down_votes',
        null         = True,
        default      = None,
    )

    #------------------------------------------------------------------------------
    # regular fields

    reliability = models.IntegerField(
        default = 5,
    )
    documentation = models.IntegerField(
        default = 5,
    )
    code_quality = models.IntegerField(
        default = 5,
    )
    wow_factor = models.IntegerField(
        default = 5,
    )
    comment = models.TextField(
        blank      = True,
        null       = True,
    )
    score = models.FloatField(
        default      = 0.0,
        editable     = False,
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

        self.reliability   = clamp_range(self.reliability)
        self.documentation = clamp_range(self.documentation)
        self.code_quality  = clamp_range(self.code_quality)
        self.wow_factor    = clamp_range(self.wow_factor)

        if len(self.comment) > 5000:
            self.comment = self.comment[:5000]

        # the value of score is based on the 
        # values in the other rating fields
        self.score = (
            self.reliability + \
            self.documentation + \
            self.code_quality + \
            self.wow_factor
        ) / 4.0
        super(RoleRating, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.pk:
            return reverse('api:rating_detail', args=(self.pk,))
        else:
            return ""

###################################################################################
# Admin Models

class PlatformAdmin(admin.ModelAdmin):
    pass
admin.site.register(Platform, PlatformAdmin)

class RoleAdmin(admin.ModelAdmin):
    pass
admin.site.register(Role, RoleAdmin)

class RoleVersionAdmin(admin.ModelAdmin):
    pass
admin.site.register(RoleVersion, RoleVersionAdmin)

class RoleImportAdmin(admin.ModelAdmin):
    pass
admin.site.register(RoleImport, RoleImportAdmin)

class RoleRatingAdmin(admin.ModelAdmin):
    pass
admin.site.register(RoleRating, RoleRatingAdmin)

class CategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(Category, CategoryAdmin)

class UserAliasAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserAlias, UserAliasAdmin)

###################################################################################
# Autofixture Classes for generating test data

if settings.SITE_ENV == 'DEV':
    from autofixture import generators, register, AutoFixture

    class WeightedRandomBoolGenerator(generators.Generator):
        """ Generates a true X% of the time """
        def __init__(self, percent_chance=100):
            if percent_chance > 100:
                percent_chance = 100
            elif percent_chance < 0:
                percent_chance = 0
            self.percent_chance = percent_chance

        def generate(self):
            return random.randrange(100) > (100 - self.percent_chance)
            

    class UserNameGenerator(generators.FirstNameGenerator, generators.LastNameGenerator):
        """ Generates a username of the form f_lname """

        def __init__(self, gender=None):
            self.gender = gender
            self.all = self.male + self.female

        def generate(self):
            if self.gender == 'm':
                first_initial = random.choice(self.male)[0].lower()
            elif self.gender == 'f':
                first_initial = random.choice(self.female)[0].lower()
            else:
                first_initial = random.choice(self.all)[0].lower()
            last_name = random.choice(self.surname).lower()
            return "%s_%s" % (first_initial, last_name)

    class FullNameGenerator(generators.FirstNameGenerator, generators.LastNameGenerator):
        """ Generates a full_name of the form 'fname lname' """

        def __init__(self, gender=None):
            self.gender = gender
            self.all = self.male + self.female

        def generate(self):
            if self.gender == 'm':
                first_name = random.choice(self.male)
            elif self.gender == 'f':
                first_name = random.choice(self.female)
            else:
                first_name = random.choice(self.all)
            last_name = random.choice(self.surname)
            return "%s %s" % (first_name, last_name)

    class RoleNameGenerator(generators.Generator):
        """ Generates a role name """

        software_packages = [
            'nginx', 'httpd', 'php', 'python', 'perl', 'ruby',
            'memcache', 'mysql', 'oracle', 'couchbase', 'hadoop',
            'cobbler', 'haproxy', 'keepalived', 
        ]

        def generate(self):
            return "testrole_%s" % random.choice(self.software_packages)

    class UserAutoFixture(AutoFixture):
        field_values = {
            'full_name': FullNameGenerator(),
            'username': UserNameGenerator(),
            'email': generators.EmailGenerator(),
            'password': generators.StaticGenerator('password'),
            'is_superuser': False,
            'is_staff': WeightedRandomBoolGenerator(percent_chance=3),
            'is_active': True,
        }
        follow_fk = False
        follow_m2m = False
    register(User, UserAutoFixture)

    class RoleAutoFixture(AutoFixture):
        field_values = {
            'name': RoleNameGenerator(),
            'github_user': generators.FirstNameGenerator(),
            'github_repo': generators.StringGenerator(min_length=6, max_length=10),
            'description': generators.LoremGenerator(max_length=250),
            'readme': generators.LoremHTMLGenerator(),
            'min_ansible_version': generators.StaticGenerator('1.3'),
            'issue_tracker_url': generators.URLGenerator(),
            'license': generators.StaticGenerator(''),
            'company': generators.StaticGenerator(''),
            'is_valid': generators.StaticGenerator(True),
        }
    register(Role, RoleAutoFixture)

    class RoleVersionAutoFixture(AutoFixture):
        choices = []
        for major in range(0,3):
            for minor in range(0,9):
                choices.append("v%d.%d" % (major,minor))
        field_values = {
            'name': generators.ChoicesGenerator(values=choices),
            'loose_version': generators.StaticGenerator("0.0"),
        }
    register(RoleVersion, RoleVersionAutoFixture)

    class RoleRatingAutoFixture(AutoFixture):
        field_values = {
            'reliability': generators.IntegerGenerator(min_value=1, max_value=5),
            'documentation': generators.IntegerGenerator(min_value=1, max_value=5),
            'code_quality': generators.IntegerGenerator(min_value=1, max_value=5),
            'wow_factor': generators.IntegerGenerator(min_value=1, max_value=5),
        }
    register(RoleRating, RoleRatingAutoFixture)
