from django.db import models, migrations

UPGRADE_SET_EMPTY_IMPORT_BRANCH_TO_NULL = """
UPDATE main_importtask
SET import_branch = NULL
WHERE import_branch = ''
"""

UPGRADE_SET_EMPTY_ALT_NAME_TO_NULL = """
UPDATE main_importtask
SET repository_alt_name = NULL
WHERE repository_alt_name = ''
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0078_auto_20180208_0629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='importtask',
            old_name='alternate_role_name',
            new_name='repository_alt_name',
        ),
        migrations.RenameField(
            model_name='importtask',
            old_name='github_reference',
            new_name='import_branch',
        ),
        migrations.RunSQL(
            sql=(UPGRADE_SET_EMPTY_IMPORT_BRANCH_TO_NULL,
                 UPGRADE_SET_EMPTY_ALT_NAME_TO_NULL),
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='importtask',
            name='import_branch',
            field=models.CharField(max_length=256, null=True, blank=False),
        ),
        migrations.AlterField(
            model_name='importtask',
            name='repository_alt_name',
            field=models.CharField(max_length=256, null=True, blank=False),
        ),
    ]
