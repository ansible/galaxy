# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0062_move_repository_counters'),
    ]

    operations = [
        migrations.RemoveField(model_name='role', name='average_score'),
        migrations.RemoveField(model_name='role', name='bayesian_score'),
        migrations.RemoveField(model_name='role', name='num_ratings'),
    ]
