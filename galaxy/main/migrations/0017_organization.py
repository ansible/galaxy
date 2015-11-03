# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import galaxy.main.fields
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0016_auto_20150922_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', galaxy.main.fields.TruncatingCharField(default=b'', max_length=255, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(unique=True, max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
                ('owner', models.ManyToManyField(related_name='organizations', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Organizations',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
    ]
