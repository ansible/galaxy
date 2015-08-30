# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20150826_1500'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='categories',
        ),
    ]
