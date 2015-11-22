# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20151119_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='importtask',
            name='finished',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
