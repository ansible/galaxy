# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


UPGRADE_INSERT_ROLE_REPOSITORIES = """
INSERT INTO main_repository (
  github_user, github_repo, is_enabled, created, modified)
SELECT github_user, github_repo, TRUE, now(), now() FROM main_role
ON CONFLICT DO NOTHING
"""

UPGRADE_ROLE_REFERENCE = """
UPDATE main_role r SET (repository_id) = (
  SELECT rp.id FROM main_repository rp
  WHERE r.github_user = rp.github_user
    AND r.github_repo = rp.github_repo
)
"""

DOWNGRADE_ROLE_REFERENCE = """
UPDATE main_role r SET (github_user, github_repo) = (
  SELECT github_user, github_repo FROM main_repository rp
  WHERE r.repository_id = rp.id
)
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0060_user_repository'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='repository',
            field=models.ForeignKey(
                related_name='role',
                editable=False,
                to='main.Repository',
                null=True,
                on_delete=models.PROTECT),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={('namespace', 'name')},
        ),
        migrations.AlterField(
            model_name='role',
            name='github_user',
            field=models.CharField(
                max_length=256,
                verbose_name="Github Username",
                null=True
            )
        ),
        migrations.AlterField(
            model_name='role',
            name='github_repo',
            field=models.CharField(
                max_length=256,
                verbose_name="Github Repository",
                null=True
            )
        ),
        migrations.RunSQL(
            sql=(UPGRADE_INSERT_ROLE_REPOSITORIES,
                 UPGRADE_ROLE_REFERENCE),
            reverse_sql=DOWNGRADE_ROLE_REFERENCE
        ),
        migrations.RemoveField(
            model_name='role',
            name='github_user',
        ),
        migrations.RemoveField(
            model_name='role',
            name='github_repo',
        ),
        migrations.AlterField(
            model_name='role',
            name='repository',
            field=models.ForeignKey(
                related_name='role',
                editable=False,
                to='main.Repository',
                on_delete=models.PROTECT),
        ),
    ]
