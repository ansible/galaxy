from django.db import models, migrations


MIGRATE_IMPORT_BRANCH = """
WITH
  it AS (
    SELECT
      it2.repository_id,
      it2.github_reference
    FROM (
      SELECT
        it1.repository_id,
        github_reference,
        ROW_NUMBER() OVER(
          PARTITION BY it1.repository_id
          ORDER BY id DESC) AS rownum
      FROM main_importtask AS it1
      WHERE github_reference != '') AS it2
    WHERE it2.rownum = 1
  ), cnt AS (
    SELECT
      c1.repository_id,
      c1.github_branch
    FROM main_content AS c1
    WHERE c1.github_branch != ''
  ), rp AS (
    SELECT
      r1.id,
      COALESCE(it.github_reference, cnt.github_branch) AS import_branch
    FROM main_repository AS r1
    LEFT JOIN it ON r1.id = it.repository_id
    LEFT JOIN cnt ON r1.id = cnt.repository_id
    WHERE COALESCE(it.github_reference, cnt.github_branch) IS NOT NULL
)
UPDATE main_repository rp2
SET import_branch = rp.import_branch
FROM rp
WHERE rp.id = rp2.id
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0073_original_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='import_branch',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.RunSQL(MIGRATE_IMPORT_BRANCH),
        migrations.RemoveField(
            model_name='content',
            name='github_branch',
        ),
        migrations.RemoveField(
            model_name='importtask',
            name='github_branch',
        ),
    ]
