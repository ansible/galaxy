# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20151102_1318'),
    ]

    operations = [
        migrations.RenameField(
            model_name='organization',
            old_name='owner',
            new_name='user',
        ),
    ]
