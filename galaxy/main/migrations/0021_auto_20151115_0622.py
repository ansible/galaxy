# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20151115_0608'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='owner',
        )
    ]
