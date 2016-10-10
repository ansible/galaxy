# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_refreshrolecount_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='refreshrolecount',
            name='skipped',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
