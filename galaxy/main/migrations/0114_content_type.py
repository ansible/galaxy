from django.db import migrations


UPDATE_PLUGIN_NAMES_SQL = """
UPDATE main_contenttype SET name = replace(name, '_plugin', '')
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0113_repository_community_score'),
    ]

    operations = [
        migrations.RunSQL(sql=(UPDATE_PLUGIN_NAMES_SQL,),
                          reverse_sql=migrations.RunSQL.noop),
    ]
