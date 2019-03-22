from django.db import migrations

REVERT_SANITIZE_NAMESPACE_NAMES = """
UPDATE main_namespace AS ns
  SET name = pns.name
FROM main_providernamespace AS pns
WHERE ns.id = pns.namespace_id
      AND pns.name LIKE '%-%'
      AND ns.name = replace(pns.name, '-', '_');
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0109_auto_20180626_1050'),
    ]

    operations = [
        migrations.RunSQL(
            sql=REVERT_SANITIZE_NAMESPACE_NAMES,
        ),
    ]
