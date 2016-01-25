# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_auto_20151125_0009'),
    ]

    operations = [
        migrations.AddField(
            model_name='importtask',
            name='commit',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='importtask',
            name='commit_message',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='importtask',
            name='commit_url',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='importtask',
            name='forks_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='importtask',
            name='open_issues_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='importtask',
            name='stargazers_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='importtask',
            name='watchers_count',
            field=models.IntegerField(default=0),
        ),
    ]
