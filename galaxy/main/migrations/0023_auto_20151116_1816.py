# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20151116_1608'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='tasks',
        ),
        migrations.AddField(
            model_name='notification',
            name='imports',
            field=models.ManyToManyField(related_name='notifications', verbose_name=b'Tasks', to='main.ImportTask'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='roles',
            field=models.ManyToManyField(related_name='notifications', verbose_name=b'Roles', to='main.Role'),
        ),
    ]
