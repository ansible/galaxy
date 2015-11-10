# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20151110_0556'),
    ]

    operations = [
        migrations.AddField(
            model_name='importtask',
            name='alternate_role_name',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Alternate Role Name', blank=True),
        ),
        migrations.AlterField(
            model_name='importtask',
            name='owner',
            field=models.ForeignKey(related_name='import_tasks', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
