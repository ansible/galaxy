# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import galaxy.main.fields
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0025_auto_20151120_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='Repository',
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
                        default=b'', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                (
                    'github_user',
                    models.CharField(
                        max_length=256, verbose_name=b'Github Username'
                    ),
                ),
                (
                    'github_repo',
                    models.CharField(
                        max_length=256, verbose_name=b'Github Repository'
                    ),
                ),
                ('is_enabled', models.BooleanField(default=False)),
                (
                    'owner',
                    models.ForeignKey(
                        related_name='repositories',
                        editable=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AlterField(
            model_name='role',
            name='bayesian_score',
            field=models.FloatField(default=0.0, editable=False),
        ),
        migrations.AlterIndexTogether(
            name='repository',
            index_together={
                ('owner', 'github_user', 'github_repo', 'is_enabled')
            },
        ),
    ]
