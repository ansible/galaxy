# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations


UPGRADE_STARGAZER_ROLE = """
UPDATE main_stargazer
SET
  role_id = main_role.id
FROM main_role
WHERE main_stargazer.github_user = main_role.github_user
  AND main_stargazer.github_repo = main_role.github_repo
"""

DELETE_STARGAZER_ROLE_ID_NULL = """
DELETE FROM main_stargazer
WHERE role_id IS NULL
"""

DOWNGRADE_STARGAZER_ROLE = """
UPDATE main_stargazer
SET
  github_user = main_role.github_user,
  github_repo = main_role.github_repo
FROM main_role
WHERE main_stargazer.role_id = main_role.id
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0056_role_unique_repos'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stargazer',
            options={},
        ),
        migrations.AddField(
            model_name='stargazer',
            name='role',
            field=models.ForeignKey(
                to='main.Role',
                null=True,
                default=None,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AlterField(
            model_name='stargazer',
            name='github_user',
            field=models.CharField(max_length=256, null=True)),
        migrations.AlterField(
            model_name='stargazer',
            name='github_repo',
            field=models.CharField(max_length=256, null=True)),
        migrations.RunSQL(sql=UPGRADE_STARGAZER_ROLE,
                          reverse_sql=DOWNGRADE_STARGAZER_ROLE),
        migrations.RunSQL(sql=DELETE_STARGAZER_ROLE_ID_NULL,
                          reverse_sql=migrations.RunSQL.noop),
        migrations.AlterField(
            model_name='stargazer',
            name='role',
            field=models.ForeignKey(to='main.Role', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='stargazer',
            unique_together={('owner', 'role')},
        ),
        migrations.RemoveField(
            model_name='stargazer',
            name='github_repo',
        ),
        migrations.RemoveField(
            model_name='stargazer',
            name='github_user',
        ),
    ]
