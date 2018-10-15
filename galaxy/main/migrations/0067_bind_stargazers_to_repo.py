# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


UPGRADE_SET_REPOSITORY_REF = """
UPDATE main_stargazer s SET repository_id = c.repository_id
FROM main_content c
WHERE s.role_id = c.id
"""

DOWNGRADE_SET_CONTENT_REF = """
UPDATE main_stargazer s SET role_id = c.id
FROM main_content c
WHERE s.repository_id = c.repository_id
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0066_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='stargazer',
            name='repository',
            field=models.ForeignKey(
                to='main.Repository',
                null=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.RunSQL(sql=UPGRADE_SET_REPOSITORY_REF,
                          reverse_sql=DOWNGRADE_SET_CONTENT_REF),
        migrations.AlterField(
            model_name='stargazer',
            name='repository',
            field=models.ForeignKey(
                to='main.Repository',
                related_name='stars',
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='stargazer',
            unique_together={('owner', 'repository')},
        ),
        migrations.RemoveField(model_name='stargazer', name='active'),
        migrations.RemoveField(model_name='stargazer', name='description'),
        migrations.RemoveField(model_name='stargazer', name='role'),
    ]
