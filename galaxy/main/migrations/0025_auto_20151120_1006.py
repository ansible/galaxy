# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_importtask_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='commit_url',
            field=models.CharField(max_length=256, blank=True),
        ),
    ]
