# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import galaxy.main.fields
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0025_auto_20151111_1101'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSecret',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', galaxy.main.fields.TruncatingCharField(default=b'', max_length=255, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('source', models.CharField(max_length=20)),
                ('secret', models.CharField(max_length=256)),
                ('owner', models.ForeignKey(related_name='notification_secrets', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('source',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.RemoveField(
            model_name='roleimport',
            name='role',
        ),
        migrations.AlterModelOptions(
            name='importtask',
            options={'ordering': ('-id',), 'get_latest_by': 'created'},
        ),
        migrations.DeleteModel(
            name='RoleImport',
        ),
        migrations.AlterUniqueTogether(
            name='notificationsecret',
            unique_together=set([('owner', 'source', 'secret')]),
        ),
    ]
