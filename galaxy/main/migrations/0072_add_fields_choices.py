from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0071_drop_original_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='repository',
            field=models.ForeignKey(
                related_name='content_objects',
                editable=False,
                to='main.Repository',
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AlterField(
            model_name='content',
            name='role_type',
            field=models.CharField(
                default='ANS', max_length=3, editable=False,
                choices=[('ANS', 'Ansible'), ('APP', 'Container App'),
                         ('CON', 'Container Enabled'), ('DEM', 'Demo')]),
        ),
        migrations.AlterField(
            model_name='contenttype',
            name='name',
            field=models.CharField(
                db_index=True, unique=True, max_length=512,
                choices=[('action_plugin', 'Action Plugin'),
                         ('cache_plugin', 'Cache Plugin'),
                         ('callback_plugin', 'Callback Plugin'),
                         ('cliconf_plugin', 'CLI Conf Plugin'),
                         ('connection_plugin', 'Connection Plugin'),
                         ('filter_plugin', 'Filter Plugin'),
                         ('inventory_plugin', 'Inventory Plugin'),
                         ('lookup_plugin', 'Lookup Plugin'),
                         ('module', 'Module'),
                         ('netconf_plugin', 'Netconf Plugin'),
                         ('role', 'Role'),
                         ('shell_plugin', 'Shell Plugin'),
                         ('strategy_plugin', 'Strategy Plugin'),
                         ('terminal_plugin', 'Terminal Plugin'),
                         ('test_plugin', 'Test Plugin')]),
        ),
        migrations.AlterField(
            model_name='importtask',
            name='state',
            field=models.CharField(
                default='PENDING', max_length=20,
                choices=[('PENDING', 'PENDING'), ('RUNNING', 'RUNNING'),
                         ('FAILED', 'FAILED'), ('SUCCESS', 'SUCCESS')]),
        ),
        migrations.AlterField(
            model_name='importtaskmessage',
            name='message_type',
            field=models.CharField(
                max_length=10,
                choices=[('ERROR', 'ERROR'), ('FAILED', 'FAILED'),
                         ('INFO', 'INFO'), ('SUCCESS', 'SUCCESS'),
                         ('WARNING', 'WARNING')]),
        ),

    ]
