# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


UPGRADE_REPLACE_ROLE_WITH_REPOSITORY = """
UPDATE main_importtask AS it
SET
  repository_id = mc.repository_id
FROM main_content AS mc
WHERE it.role_id = mc.id
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0068_auto_20180102_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='importtask',
            name='repository',
            field=models.ForeignKey(
                related_name='import_tasks',
                null=True, default=None,
                to='main.Repository',
                on_delete=models.CASCADE,
            ),
            preserve_default=False,
        ),
        # NOTE(cutwater): Due to ambiguity in the next migrations
        # rollback for this migration is prohibited.
        migrations.RunSQL(UPGRADE_REPLACE_ROLE_WITH_REPOSITORY),
        migrations.AlterField(
            model_name='importtask',
            name='repository',
            field=models.ForeignKey(
                related_name='import_tasks',
                to='main.Repository',
                on_delete=models.CASCADE,
            ),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='importtask',
            name='role',
        )
    ]
