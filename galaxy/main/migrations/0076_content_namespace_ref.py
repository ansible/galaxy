# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


UPGRADE_SET_CONTENT_NAMESPACE_REF = """
UPDATE main_content c
SET namespace_id = ns.id
FROM main_namespace ns
WHERE c.namespace_old = ns.name
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0075_repo_namespace_ref'),
    ]

    operations = [
        migrations.RenameField(
            model_name='content',
            old_name='namespace',
            new_name='namespace_old',
        ),
        migrations.AddField(
            model_name='content',
            name='namespace',
            field=models.ForeignKey(
                to='main.Namespace',
                null=True),
        ),
        migrations.RunSQL(sql=UPGRADE_SET_CONTENT_NAMESPACE_REF),
        migrations.AlterField(
            model_name='content',
            name='namespace',
            field=models.ForeignKey(
                related_name='content_objects',
                to='main.Namespace'),
        ),
        migrations.AlterUniqueTogether(
            name='content',
            unique_together={('namespace', 'content_type', 'name')},
        ),
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ('namespace', 'content_type', 'name')},
        ),
        migrations.RemoveField(
            model_name='content',
            name='namespace_old'
        )
    ]
