# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_role_type_demo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.SlugField()),
                ('title', models.CharField(max_length=256, verbose_name=b'title', blank=True)),
                ('image', models.CharField(max_length=256, verbose_name=b'image', blank=True)),
                ('content', models.TextField(verbose_name=b'content', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
    ]
