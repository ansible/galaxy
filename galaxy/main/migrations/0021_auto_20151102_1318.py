# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20151102_1315'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('organization', 'name')]),
        ),
        migrations.RemoveField(
            model_name='role',
            name='owner',
        ),
    ]
