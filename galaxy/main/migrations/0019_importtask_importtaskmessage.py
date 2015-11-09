# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.mixins
import galaxy.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20151104_1701'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', galaxy.main.fields.TruncatingCharField(default=b'', max_length=255, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('github_user', models.CharField(max_length=256, verbose_name=b'Github Username')),
                ('github_repo', models.CharField(max_length=256, verbose_name=b'Github Repository')),
                ('celery_task_id', models.CharField(default=b'', max_length=100, editable=False, db_index=True, blank=True)),
                ('state', models.CharField(default=b'', max_length=20, db_index=True, blank=True)),
                ('started', models.DateTimeField()),
                ('role', models.ForeignKey(related_name='import_tasks', default=None, blank=True, to='main.Role', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='ImportTaskMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', galaxy.main.fields.TruncatingCharField(default=b'', max_length=255, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('message_type', models.CharField(max_length=10, editable=False)),
                ('message_text', models.CharField(max_length=256, editable=False)),
                ('task', models.ForeignKey(related_name='messages', to='main.ImportTask')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
    ]
