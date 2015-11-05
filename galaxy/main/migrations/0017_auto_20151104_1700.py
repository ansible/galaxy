# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20150922_1041'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='authors',
        ),
        migrations.AddField(
            model_name='role',
            name='namespace',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Namespace', blank=True),
        ),
    ]
