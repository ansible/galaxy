# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_auto_20151122_0827'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='repository',
            options={'ordering': ('github_user', 'github_repo')},
        ),
        migrations.AddField(
            model_name='role',
            name='imported',
            field=models.DateTimeField(null=True, verbose_name=b'Last Import'),
        ),
        migrations.AlterIndexTogether(
            name='repository',
            index_together=set([('github_user', 'github_repo'), ('owner', 'github_user', 'github_repo', 'is_enabled')]),
        )
    ]
