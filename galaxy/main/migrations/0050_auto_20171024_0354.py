# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.fields
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0049_auto_20161013_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', galaxy.main.fields.TruncatingCharField(default=b'', max_length=255, blank=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('url', models.CharField(unique=True, max_length=256)),
            ],
            options={
                'verbose_name': 'videos',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AddField(
            model_name='role',
            name='videos',
            field=models.ManyToManyField(related_name='videos', verbose_name=b'videos', editable=False, to='main.Video', blank=True),
        ),
    ]
