# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_role_github_branch'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='github_branch',
            field=models.CharField(max_length=256, verbose_name=b'GitHub Branch', blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='messages',
            field=django.contrib.postgres.fields.ArrayField(default=list, base_field=models.CharField(max_length=256), size=None),
        ),
    ]
