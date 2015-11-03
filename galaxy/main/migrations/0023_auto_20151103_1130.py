# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20151102_2222'),
    ]

    operations = [
        migrations.RenameField(
            model_name='organization',
            old_name='user',
            new_name='users',
        ),
    ]
