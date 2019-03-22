from django.db import migrations, models

UPGRADE_SET_TRAVIS_URLS = """
UPDATE main_repository r
SET travis_status_url = c.travis_status_url,
    travis_build_url = c.travis_build_url
FROM main_content c
WHERE r.id = c.repository_id
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0085_auto_20180328_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='travis_build_url',
            field=models.CharField(blank=True, default='', max_length=256,
                                   verbose_name='Travis Build URL'),
        ),
        migrations.AddField(
            model_name='repository',
            name='travis_status_url',
            field=models.CharField(blank=True, default='', max_length=256,
                                   verbose_name='Travis Build Status'),
        ),
        migrations.RunSQL(
            sql=(
                UPGRADE_SET_TRAVIS_URLS,
            ),
            reverse_sql=migrations.RunSQL.noop),
    ]
