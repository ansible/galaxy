# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20151115_0622'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='role',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='task',
        ),
        migrations.AddField(
            model_name='notification',
            name='roles',
            field=models.ManyToManyField(related_name='notifications', null=True, verbose_name=b'Roles', to='main.Role'),
        ),
        migrations.AddField(
            model_name='notification',
            name='tasks',
            field=models.ManyToManyField(related_name='notifications', null=True, verbose_name=b'Tasks', to='main.ImportTask'),
        ),
    ]
