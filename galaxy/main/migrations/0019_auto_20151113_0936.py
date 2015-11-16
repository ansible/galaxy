# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.mixins
from django.conf import settings
import galaxy.main.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
                ('github_reference', models.CharField(max_length=256, verbose_name=b'Github Reference')),
                ('alternate_role_name', models.CharField(max_length=256, null=True, verbose_name=b'Alternate Role Name', blank=True)),
                ('celery_task_id', models.CharField(max_length=100, null=True, blank=True)),
                ('state', models.CharField(default=b'PENDING', max_length=20)),
                ('started', models.DateTimeField(null=True, blank=True)),
                ('owner', models.ForeignKey(related_name='import_tasks', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(related_name='import_tasks', to='main.Role')),
            ],
            options={
                'ordering': ('-id',),
                'get_latest_by': 'created',
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
                ('message_type', models.CharField(max_length=10)),
                ('message_text', models.CharField(max_length=256)),
                ('task', models.ForeignKey(related_name='messages', to='main.ImportTask')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', galaxy.main.fields.TruncatingCharField(default=b'', max_length=255, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('source', models.CharField(max_length=20)),
                ('owner', models.ForeignKey(related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(related_name='notifications', to='main.Role')),
                ('task', models.ForeignKey(related_name='notifications', to='main.ImportTask', null=True)),
            ],
            options={
                'ordering': ('-id',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
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
                ('owner', models.ForeignKey(related_name='notification_secrets', to=settings.AUTH_USER_MODEL)),
                ('github_repo',models.CharField(max_length=256)),
                ('github_user',models.CharField(max_length=256)),
            ],
            options={
                'ordering': ('source',),
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['namespace', 'name']},
        ),
        migrations.AlterField(
            model_name='role',
            name='is_valid',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='role',
            name='license',
            field=models.CharField(max_length=50, verbose_name=b'License (optional)', blank=True),
        ),
        migrations.RemoveField(
            model_name='roleimport',
            name='role',
        ),
        migrations.DeleteModel(
            name='RoleImport',
        )
    ]
