# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_auto_20160206_0921'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together=set([('owner', 'github_user', 'github_repo')]),
        ),
        migrations.AlterIndexTogether(
            name='repository',
            index_together=set([]),
        )
    ]
