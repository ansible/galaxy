# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.fields
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_auto_20171108_2113'),
    ]

    operations = [
        migrations.CreateModel(
            name='CloudPlatform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default=b'', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(unique=True, max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AddField(
            model_name='role',
            name='cloud_platforms',
            field=models.ManyToManyField(related_name='roles',
                                         verbose_name=b'Cloud Platforms',
                                         editable=False,
                                         to='main.CloudPlatform', blank=True),
        ),
    ]
