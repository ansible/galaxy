# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_auto_20151203_0014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roleversion',
            name='release_date',
        ),
    ]
