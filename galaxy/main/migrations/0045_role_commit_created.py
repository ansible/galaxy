# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0044_auto_20160916_0839')]

    operations = [
        migrations.AddField(
            model_name='role',
            name='commit_created',
            field=models.DateTimeField(
                null=True, verbose_name='Laste Commit DateTime'
            ),
        )
    ]
