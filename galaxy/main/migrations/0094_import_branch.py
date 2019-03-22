from django.db import migrations


UPGRADE_SET_IMPORT_BRANCH_DEFAULT_VALUE = """
UPDATE main_repository
SET import_branch = 'master'
WHERE import_branch IS NULL
"""


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0093_link_content_version_w_repo'),
    ]

    operations = [
        migrations.RunSQL(
            sql=UPGRADE_SET_IMPORT_BRANCH_DEFAULT_VALUE,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
