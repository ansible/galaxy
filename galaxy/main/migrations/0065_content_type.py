# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import galaxy.main.mixins
from django.utils.timezone import utc
import galaxy.main.fields

UPGRADE_INSERT_CONTENT_TYPES = """
INSERT INTO main_contenttype 
  (name, description, created, modified)
VALUES
    ('action_plugin', 'Action_plugin', now(), now()),
    ('cache_plugin', 'Cache plugin', now(), now()),
    ('callback_plugin', 'Callback plugin', now(), now()),
    ('cliconf_plugin', 'CLI config plugin', now(), now()),
    ('connection_plugin', 'Connection plugin', now(), now()),
    ('filter_plugin', 'Filter plugin', now(), now()),
    ('inventory_plugin', 'Inventory plugin', now(), now()),
    ('lookup_plugin', 'Lookup plugin', now(), now()),
    ('module', 'Module', now(), now()),
    ('netconf_plugin', 'Netconf plugin', now(), now()),
    ('role', 'Role', now(), now()),
    ('shell_plugin', 'Shell plugin', now(), now()),
    ('strategy_plugin', 'Strategy plugin', now(), now()),
    ('terminal_plugin', 'Terminal plugin', now(), now()),
    ('test_plugin', 'Test plugin', now(), now())
"""

UPGRADE_SET_ROLES_CONTENT_TYPE = """
UPDATE main_content SET content_type_id = (
  SELECT id FROM main_contenttype WHERE name = 'role'
)
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0064_rename_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(unique=True, max_length=512,
                                          db_index=True)),
                ('description', galaxy.main.fields.TruncatingCharField(
                    default=b'', max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AddField(
            model_name='content',
            name='content_type',
            field=models.ForeignKey(
                to='main.ContentType',
                null=True
            ),
        ),
        migrations.RunSQL(sql=(UPGRADE_INSERT_CONTENT_TYPES,
                               UPGRADE_SET_ROLES_CONTENT_TYPE),
                          reverse_sql=migrations.RunSQL.noop),
        migrations.AlterField(
            model_name='content',
            name='content_type',
            field=models.ForeignKey(
                to='main.ContentType',
                related_name='content_objects',
                editable=False,
                on_delete=models.PROTECT,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='content',
            unique_together={('content_type', 'namespace', 'name')},
        ),
    ]
