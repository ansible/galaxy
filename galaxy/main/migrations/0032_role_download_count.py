# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20151129_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='download_count',
            field=models.IntegerField(default=0),
        ),
    ]
