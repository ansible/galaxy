# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0020_auto_20151105_2252'),
    ]

    operations = [
        migrations.AddField(
            model_name='importtask',
            name='owner',
            field=models.ForeignKey(related_name='import_tasks', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
