from django.db import migrations, models


UPGRADE_SET_FORMAT_FOR_ROLE_REPOS = """
UPDATE main_repository
SET "format" = 'role'
WHERE id IN (
  SELECT DISTINCT c.repository_id FROM main_content c
  JOIN main_contenttype ct on c.content_type_id = ct.id
  WHERE
    ct.name = 'role' AND
    c.repository_id IN (
      SELECT repository_id FROM main_content
      GROUP BY repository_id HAVING count(*) = 1
    )
)
"""

UPGRADE_SET_FORMAT_FOR_APB_REPOS = """
UPDATE main_repository
SET "format" = 'apb'
WHERE id IN (
  SELECT DISTINCT c.repository_id FROM main_content c
  JOIN main_contenttype ct on c.content_type_id = ct.id
  WHERE
    ct.name = 'apb' AND
    c.repository_id IN (
      SELECT repository_id FROM main_content
      GROUP BY repository_id HAVING count(*) = 1
    )
)
"""

UPGRADE_SET_FORMAT_FOR_MULTI_REPOS = """
UPDATE main_repository
SET "format" = 'multi'
WHERE id IN (
  SELECT DISTINCT c.repository_id FROM main_content c
  JOIN main_contenttype ct on c.content_type_id = ct.id
  WHERE
    ct.name NOT IN ('role', 'apb') OR
    c.repository_id IN (
      SELECT repository_id FROM main_content
      GROUP BY repository_id HAVING count(*) > 1
    )
)
"""


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0095_repository_version_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='format',
            field=models.CharField(
                max_length=16,
                null=True,
                choices=[
                    ('role', 'Role'),
                    ('apb', 'Ansible Playbook Bundle'),
                    ('multi', 'Multi-content')
                ]),
            preserve_default=False,
        ),
        migrations.RunSQL(sql=[
            UPGRADE_SET_FORMAT_FOR_APB_REPOS,
            UPGRADE_SET_FORMAT_FOR_ROLE_REPOS,
            UPGRADE_SET_FORMAT_FOR_MULTI_REPOS,
        ], reverse_sql=migrations.RunSQL.noop)
    ]
