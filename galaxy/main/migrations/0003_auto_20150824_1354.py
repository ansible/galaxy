# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150824_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='average_score',
            field=models.FloatField(default=0.0, editable=False),
        ),
        migrations.AddField(
            model_name='role',
            name='num_ratings',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
