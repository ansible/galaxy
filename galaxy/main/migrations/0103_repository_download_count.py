from django.db import migrations, models

UPGRADE_REPOSITORY_DOWNLOAD_COUNTS = """
UPDATE main_repository r SET download_count = (
  SELECT coalesce(sum(download_count), 0) FROM main_content c
  WHERE r.id = c.repository_id
);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0102_provider_download_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='download_count',
            field=models.IntegerField(default=0),
        ),
        migrations.RunSQL(UPGRADE_REPOSITORY_DOWNLOAD_COUNTS),
        migrations.RemoveField(
            model_name='content',
            name='download_count'
        )
    ]
