# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_importtask_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='importtask',
            old_name='owner',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='importtask',
            name='role',
            field=models.ForeignKey(related_name='import_tasks', default=None, blank=True, editable=False, to='main.Role', null=True),
        ),
    ]
