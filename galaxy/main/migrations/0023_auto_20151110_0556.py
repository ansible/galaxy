# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20151110_0456'),
    ]

    operations = [
        migrations.RenameField(
            model_name='importtask',
            old_name='user',
            new_name='owner',
        ),
    ]
