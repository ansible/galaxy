# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

UPGRADE_FIX_CONTENT_EMPTY_NAME = """
UPDATE main_content c
SET name = r.original_name
FROM main_repository r
WHERE c.repository_id = r.id AND c.name = ''
"""

UPGRADE_REPOSITORY_ALIAS = """
WITH r1 AS (
  SELECT
    r.id,
    COALESCE(c.name, r.original_name) AS name
FROM main_repository r
LEFT JOIN main_content c
    ON r.id = c.repository_id
    AND c.is_valid = TRUE
)
UPDATE main_repository AS r2
SET name = r1.name
FROM r1
WHERE r1.id = r2.id
"""

UPGRADE_SET_CONTENT_ORIGINAL_NAME = """
UPDATE main_content SET original_name = name
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0072_add_fields_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='github_repo',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='repository',
            name='github_user',
            field=models.CharField(max_length=256),
        ),
        migrations.RenameField(
            model_name='repository',
            old_name='github_repo',
            new_name='original_name',
        ),
        migrations.AddField(
            model_name='repository',
            name='name',
            field=models.CharField(max_length=256, null=False, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='content',
            name='original_name',
            field=models.CharField(max_length=256, null=False, default=''),
            preserve_default=False,
        ),
        migrations.RunSQL(
            sql=(
                UPGRADE_FIX_CONTENT_EMPTY_NAME,
                UPGRADE_REPOSITORY_ALIAS,
                UPGRADE_SET_CONTENT_ORIGINAL_NAME
            ),
            reverse_sql=migrations.RunSQL.noop),
    ]
