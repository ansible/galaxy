# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0028_auto_20151125_1231')]

    operations = [
        migrations.AddField(
            model_name='importtask',
            name='github_branch',
            field=models.CharField(
                default=b'',
                max_length=256,
                verbose_name=b'Github Branch',
                blank=True,
            ),
        )
    ]
