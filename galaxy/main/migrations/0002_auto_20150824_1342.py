# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rolerating',
            name='code_quality',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='documentation',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='down_votes',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='reliability',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='up_votes',
        ),
        migrations.RemoveField(
            model_name='rolerating',
            name='wow_factor',
        ),
    ]
