# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0039_namespace')]

    operations = [
        migrations.AddField(
            model_name='role',
            name='readme_type',
            field=models.CharField(
                max_length=5, null=True, verbose_name=b'README type'
            ),
        ),
        migrations.AlterField(
            model_name='role',
            name='readme',
            field=models.TextField(
                default=b'', verbose_name=b'README content', blank=True
            ),
        ),
    ]
