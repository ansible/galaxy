# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.fields
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [('main', '0038_role_github_default_branch')]

    operations = [
        migrations.CreateModel(
            name='Namespace',
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
                    'namespace',
                    models.CharField(
                        unique=True,
                        max_length=256,
                        verbose_name='GitHub namespace',
                        db_index=True,
                    ),
                ),
                (
                    'name',
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name='GitHub name',
                        blank=True,
                    ),
                ),
                (
                    'avatar_url',
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name='GitHub Avatar URL',
                        blank=True,
                    ),
                ),
                (
                    'location',
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name='Location',
                        blank=True,
                    ),
                ),
                (
                    'company',
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name='Location',
                        blank=True,
                    ),
                ),
                (
                    'email',
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name='Location',
                        blank=True,
                    ),
                ),
                (
                    'html_url',
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name='URL',
                        blank=True,
                    ),
                ),
                (
                    'followers',
                    models.IntegerField(null=True, verbose_name='Followers'),
                ),
            ],
            options={'ordering': ('namespace',)},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        )
    ]
