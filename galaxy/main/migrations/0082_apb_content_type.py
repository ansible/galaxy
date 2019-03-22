from django.db import models, migrations

INSERT_APB_CONTENT_TYPE = """
INSERT INTO main_contenttype
  (name, description, created, modified)
VALUES
  ('apb', 'Ansible Playbook Bundle', now(), now())
"""

DELETE_APB_CONTENT_TYPE = """
DELETE FROM main_contenttype WHERE name = 'apb'
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0081_content_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='role_type',
            field=models.CharField(
                default=None, max_length=3, null=True,
                editable=False, choices=[
                    ('ANS', 'Ansible'),
                    ('APP', 'Container App'),
                    ('CON', 'Container Enabled'),
                    ('DEM', 'Demo')]),
        ),
        migrations.AlterField(
            model_name='contenttype',
            name='name',
            field=models.CharField(
                db_index=True,
                unique=True,
                max_length=512,
                choices=[('action_plugin', 'Action Plugin'),
                         ('apb', 'Ansible Playbook Bundle'),
                         ('cache_plugin', 'Cache Plugin'),
                         ('callback_plugin', 'Callback Plugin'),
                         ('cliconf_plugin', 'CLI Conf Plugin'),
                         ('connection_plugin', 'Connection Plugin'),
                         ('filter_plugin', 'Filter Plugin'),
                         ('inventory_plugin', 'Inventory Plugin'),
                         ('lookup_plugin', 'Lookup Plugin'),
                         ('module', 'Module'),
                         ('netconf_plugin', 'Netconf Plugin'),
                         ('role', 'Role'), ('shell_plugin', 'Shell Plugin'),
                         ('strategy_plugin', 'Strategy Plugin'),
                         ('terminal_plugin', 'Terminal Plugin'),
                         ('test_plugin', 'Test Plugin')]),
        ),
        migrations.RunSQL(sql=INSERT_APB_CONTENT_TYPE,
                          reverse_sql=DELETE_APB_CONTENT_TYPE),
    ]
