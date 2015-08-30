# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20150826_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=models.CharField(max_length=256), size=100),
        ),
    ]
