from django.db import migrations

DELETE_DUPLICATE_REPOSITORY_VERSIONS = """
DELETE FROM main_repositoryversion
WHERE id IN (
  SELECT t.id FROM (
    SELECT id, ROW_NUMBER() OVER (
      PARTITION BY name, repository_id ORDER BY id) AS rownum
    FROM main_repositoryversion
  ) AS t
  WHERE t.rownum > 1
)
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0094_import_branch'),
    ]

    operations = [
        migrations.RunSQL(sql=DELETE_DUPLICATE_REPOSITORY_VERSIONS,
                          reverse_sql=migrations.RunSQL.noop),
        migrations.AlterUniqueTogether(
            name='repositoryversion',
            unique_together={('repository', 'name')},
        ),
    ]
