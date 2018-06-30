# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_refreshrolecount_skipped'),
    ]

    operations = [
        migrations.RenameField(
            model_name='refreshrolecount',
            old_name='skipped',
            new_name='updated',
        ),
    ]
