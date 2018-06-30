from __future__ import unicode_literals

from django.db import migrations, models


UPGRADE_CONTENT_VERSION_REPOSITORY_REF = """
UPDATE main_repositoryversion cv SET (repository_id) = (
  SELECT DISTINCT c.repository_id
  FROM main_content c
  WHERE cv.content_id = c.id
)
"""


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0092_content_module_utils'),
    ]

    operations = [
        migrations.RenameModel(
            'ContentVersion',
            'RepositoryVersion'
        ),
        migrations.AddField(
            model_name='repositoryversion',
            name='repository',
            field=models.ForeignKey(
                to='main.Repository',
                related_name='versions',
                null=True
            ),
        ),
        migrations.RunSQL(
            sql=UPGRADE_CONTENT_VERSION_REPOSITORY_REF,
        ),
        migrations.AlterField(
            model_name='repositoryversion',
            name='repository',
            field=models.ForeignKey(
                to='main.Repository',
                related_name='versions',
            ),
        ),
        migrations.RemoveField(
            model_name='repositoryversion',
            name='content',
        ),
    ]
