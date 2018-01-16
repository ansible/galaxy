# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0069_importtask_repository_ref'),
    ]

    operations = [
        migrations.RemoveField(model_name='importtask',
                               name='github_user'),
        migrations.RemoveField(model_name='importtask',
                               name='github_repo'),
        migrations.RemoveField(model_name='importtask',
                               name='forks_count'),
        migrations.RemoveField(model_name='importtask',
                               name='open_issues_count'),
        migrations.RemoveField(model_name='importtask',
                               name='stargazers_count'),
        migrations.RemoveField(model_name='importtask',
                               name='watchers_count'),
    ]
