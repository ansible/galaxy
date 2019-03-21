# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.mixins
from django.conf import settings
import galaxy.main.fields


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Category',
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
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                (
                    'name',
                    models.CharField(
                        unique=True, max_length=512, db_index=True
                    ),
                ),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Platform',
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
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
                (
                    'release',
                    models.CharField(
                        max_length=50,
                        verbose_name='Distribution Release Version',
                    ),
                ),
            ],
            options={'ordering': ['name', 'release']},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Role',
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
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
                (
                    'github_user',
                    models.CharField(
                        max_length=256, verbose_name='Github Username'
                    ),
                ),
                (
                    'github_repo',
                    models.CharField(
                        max_length=256, verbose_name='Github Repository'
                    ),
                ),
                ('readme', models.TextField(default='', blank=True)),
                (
                    'min_ansible_version',
                    models.CharField(
                        max_length=10,
                        null=True,
                        verbose_name='Minimum Ansible Version Required',
                        blank=True,
                    ),
                ),
                (
                    'issue_tracker_url',
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name='Issue Tracker URL',
                        blank=True,
                    ),
                ),
                (
                    'license',
                    models.CharField(
                        max_length=30,
                        verbose_name='License (optional)',
                        blank=True,
                    ),
                ),
                (
                    'company',
                    models.CharField(
                        max_length=50,
                        null=True,
                        verbose_name='Company Name (optional)',
                        blank=True,
                    ),
                ),
                (
                    'is_valid',
                    models.BooleanField(default=False, db_index=True),
                ),
                (
                    'featured',
                    models.BooleanField(default=False, editable=False),
                ),
                (
                    'bayesian_score',
                    models.FloatField(
                        default=0.0, editable=False, db_index=True
                    ),
                ),
                (
                    'authors',
                    models.ManyToManyField(
                        related_name='author_on',
                        editable=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'categories',
                    models.ManyToManyField(
                        related_name='roles',
                        editable=False,
                        to='main.Category',
                        blank=True,
                        help_text='',
                        verbose_name='Categories',
                    ),
                ),
                (
                    'dependencies',
                    models.ManyToManyField(
                        related_name='+',
                        editable=False,
                        to='main.Role',
                        blank=True,
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        related_name='roles',
                        editable=False,
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    'platforms',
                    models.ManyToManyField(
                        related_name='roles',
                        editable=False,
                        to='main.Platform',
                        blank=True,
                        help_text='',
                        verbose_name='Supported Platforms',
                    ),
                ),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='RoleImport',
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
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                (
                    'celery_task_id',
                    models.CharField(
                        default='',
                        max_length=100,
                        editable=False,
                        db_index=True,
                        blank=True,
                    ),
                ),
                ('released', models.DateTimeField(auto_now_add=True)),
                (
                    'state',
                    models.CharField(
                        default='', max_length=20, db_index=True, blank=True
                    ),
                ),
                (
                    'status_message',
                    models.CharField(default='', max_length=512, blank=True),
                ),
                (
                    'role',
                    models.ForeignKey(
                        related_name='imports',
                        to='main.Role',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={'get_latest_by': 'released'},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='RoleRating',
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
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('reliability', models.IntegerField(default=5)),
                ('documentation', models.IntegerField(default=5)),
                ('code_quality', models.IntegerField(default=5)),
                ('wow_factor', models.IntegerField(default=5)),
                ('comment', models.TextField(null=True, blank=True)),
                (
                    'score',
                    models.FloatField(
                        default=0.0, editable=False, db_index=True
                    ),
                ),
                (
                    'down_votes',
                    models.ManyToManyField(
                        default=None,
                        related_name='user_down_votes',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        related_name='ratings',
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    'role',
                    models.ForeignKey(
                        related_name='ratings',
                        to='main.Role',
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    'up_votes',
                    models.ManyToManyField(
                        default=None,
                        related_name='user_up_votes',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='RoleVersion',
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
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
                ('release_date', models.DateTimeField(null=True, blank=True)),
                (
                    'loose_version',
                    galaxy.main.fields.LooseVersionField(
                        editable=False, db_index=True
                    ),
                ),
                (
                    'role',
                    models.ForeignKey(
                        related_name='versions',
                        to='main.Role',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={'ordering': ('-loose_version',)},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='UserAlias',
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
                ('alias_name', models.CharField(unique=True, max_length=30)),
                (
                    'alias_of',
                    models.ForeignKey(
                        related_name='aliases',
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={'verbose_name_plural': 'UserAliases'},
        ),
        migrations.AlterUniqueTogether(
            name='rolerating', unique_together=set([('owner', 'role')])
        ),
        migrations.AlterUniqueTogether(
            name='role', unique_together=set([('owner', 'name')])
        ),
    ]
