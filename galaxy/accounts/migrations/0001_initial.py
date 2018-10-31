# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
import django.contrib.auth.models
import galaxy.main.mixins
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [('auth', '0006_require_contenttypes_0002')]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'password',
                    models.CharField(max_length=128, verbose_name='password'),
                ),
                (
                    'last_login',
                    models.DateTimeField(
                        null=True, verbose_name='last login', blank=True
                    ),
                ),
                (
                    'is_superuser',
                    models.BooleanField(
                        default=False,
                        help_text='Designates that this user has all '
                                  'permissions without explicitly '
                                  'assigning them.',
                        verbose_name='superuser status',
                    ),
                ),
                (
                    'username',
                    models.CharField(
                        help_text='Required. 30 characters or fewer. '
                                  'Letters, numbers and @/./+/-/_ characters',
                        unique=True,
                        max_length=30,
                        verbose_name='username',
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile(r'^[a-zA-Z0-9_.@+-]+$'),
                                'Enter a valid username.',
                                'invalid',
                            )
                        ],
                    ),
                ),
                (
                    'full_name',
                    models.CharField(
                        max_length=254, verbose_name='full name', blank=True
                    ),
                ),
                (
                    'short_name',
                    models.CharField(
                        max_length=30, verbose_name='short name', blank=True
                    ),
                ),
                (
                    'email',
                    models.EmailField(
                        unique=True,
                        max_length=254,
                        verbose_name='email address',
                    ),
                ),
                (
                    'is_staff',
                    models.BooleanField(
                        default=False,
                        help_text='Designates whether the user can log into '
                                  'this admin site.',
                        verbose_name='staff status',
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=True,
                        help_text='Designates whether this user should be '
                                  'treated as active. Unselect this instead '
                                  'of deleting accounts.',
                        db_index=True,
                        verbose_name='active',
                    ),
                ),
                (
                    'date_joined',
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name='date joined',
                    ),
                ),
                ('karma', models.IntegerField(default=0, db_index=True)),
                (
                    'groups',
                    models.ManyToManyField(
                        related_query_name='user',
                        related_name='user_set',
                        to='auth.Group',
                        blank=True,
                        help_text='The groups this user belongs to. '
                                  'A user will get all permissions granted '
                                  'to each of their groups.',
                        verbose_name='groups',
                    ),
                ),
                (
                    'user_permissions',
                    models.ManyToManyField(
                        related_query_name='user',
                        related_name='user_set',
                        to='auth.Permission',
                        blank=True,
                        help_text='Specific permissions for this user.',
                        verbose_name='user permissions',
                    ),
                ),
            ],
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
            managers=[('objects', django.contrib.auth.models.UserManager())],
        )
    ]
