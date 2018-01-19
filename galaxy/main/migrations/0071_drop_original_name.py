# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0070_remove_importtask_github_counters'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='original_name',
        ),
        migrations.RemoveField(
            model_name='cloudplatform',
            name='original_name',
        ),
        migrations.RemoveField(
            model_name='content',
            name='original_name',
        ),
        migrations.RemoveField(
            model_name='contentversion',
            name='original_name',
        ),
        migrations.RemoveField(
            model_name='namespace',
            name='original_name',
        ),
        migrations.RemoveField(
            model_name='platform',
            name='original_name',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='original_name',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='original_name',
        ),
    ]
