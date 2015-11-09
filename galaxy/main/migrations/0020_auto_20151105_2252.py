# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_importtask_importtaskmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importtask',
            name='celery_task_id',
            field=models.CharField(db_index=True, max_length=100, null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='importtask',
            name='started',
            field=models.DateTimeField(null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='importtask',
            name='state',
            field=models.CharField(default=b'', editable=False, max_length=20, blank=True, null=True, db_index=True),
        ),
    ]
