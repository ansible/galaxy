from django.db import migrations, models

GITHUB_DOWNLOAD_URL = (
    "https://github.com/{username}/{repository}/archive/{ref}.tar.gz"
)

UPGRADE_GITHUB_DOWNLOAD_URL = """
UPDATE main_provider SET download_url = '{}' WHERE name = 'GitHub'
""".format(GITHUB_DOWNLOAD_URL)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0101_remove_importtask_repository_alt_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='download_url',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.RunSQL(sql=UPGRADE_GITHUB_DOWNLOAD_URL,
                          reverse_sql=migrations.RunSQL.noop)
    ]
