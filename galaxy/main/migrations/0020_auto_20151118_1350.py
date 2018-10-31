# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0019_auto_20151113_0936')]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='commit',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='commit_message',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='committed_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='travis_build_url',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='role',
            name='travis_status_url',
            field=models.CharField(
                default='',
                max_length=256,
                verbose_name='Travis Build Status',
                blank=True,
            ),
        ),
    ]
