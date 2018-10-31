# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0035_remove_roleversion_release_date')]

    operations = [
        migrations.AddField(
            model_name='importtask',
            name='travis_build_url',
            field=models.CharField(
                default='',
                max_length=256,
                verbose_name='Travis Build URL',
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name='importtask',
            name='travis_status_url',
            field=models.CharField(
                default='',
                max_length=256,
                verbose_name='Travis Build Status',
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name='notification',
            name='travis_status',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='role',
            name='travis_build_url',
            field=models.CharField(
                default='',
                max_length=256,
                verbose_name='Travis Build URL',
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='importtask',
            name='github_reference',
            field=models.CharField(
                default='',
                max_length=256,
                null=True,
                verbose_name='Github Reference',
                blank=True,
            ),
        ),
    ]
