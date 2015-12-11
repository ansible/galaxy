# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_roleversion_release_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='github_default_branch',
            field=models.CharField(default=b'master', max_length=256, verbose_name=b'Default Branch'),
        ),
    ]
