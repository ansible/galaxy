# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20151104_1701'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('github_user', 'name')]),
        ),
        migrations.RemoveField(
            model_name='role',
            name='namespace',
        ),
    ]
