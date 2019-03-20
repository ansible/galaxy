# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.mixins
from django.conf import settings
import django.contrib.postgres.fields
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
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                (
                    'github_user',
                    models.CharField(
                        max_length=256, verbose_name='Github Username'
                    ),
                ),
                (
                    'github_repo',
                    models.CharField(
                        max_length=256, verbose_name='Github Repository'
                    ),
                ),
                (
                    'github_reference',
                    models.CharField(
                        max_length=256, verbose_name='Github Reference'
                    ),
                ),
                (
                    'alternate_role_name',
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name='Alternate Role Name',
                        blank=True,
                    ),
                ),
                (
                    'celery_task_id',
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ('state', models.CharField(default='PENDING', max_length=20)),
                ('started', models.DateTimeField(null=True, blank=True)),
                (
                    'owner',
                    models.ForeignKey(
                        related_name='import_tasks',
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    'role',
                    models.ForeignKey(
                        related_name='import_tasks',
                        to='main.Role',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={'ordering': ('-id',), 'get_latest_by': 'created'},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='ImportTaskMessage',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('message_type', models.CharField(max_length=10)),
                ('message_text', models.CharField(max_length=256)),
                (
                    'task',
                    models.ForeignKey(
                        related_name='messages',
                        to='main.ImportTask',
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={'abstract': False},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                (
                    'source',
                    models.CharField(
                        max_length=20, verbose_name='Source', editable=False
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        related_name='notifications',
                        to=settings.AUTH_USER_MODEL,
                        editable=False,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    'roles',
                    models.ManyToManyField(
                        related_name='notifications',
                        verbose_name='Roles',
                        to='main.Role',
                        editable=False,
                    ),
                ),
                (
                    'imports',
                    models.ManyToManyField(
                        related_name='notifications',
                        verbose_name='Tasks',
                        to='main.ImportTask',
                        editable=False,
                    ),
                ),
                (
                    'github_branch',
                    models.CharField(
                        max_length=256,
                        verbose_name='GitHub Branch',
                        blank=True,
                        editable=False,
                    ),
                ),
                (
                    'messages',
                    django.contrib.postgres.fields.ArrayField(
                        default=list,
                        base_field=models.CharField(max_length=256),
                        size=None,
                        editable=False,
                    ),
                ),
            ],
            options={'ordering': ('-id',)},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.CreateModel(
            name='NotificationSecret',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                (
                    'source',
                    models.CharField(max_length=20, verbose_name='Source'),
                ),
                (
                    'secret',
                    models.CharField(
                        max_length=256, verbose_name='Secret', db_index=True
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        related_name='notification_secrets',
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    'github_repo',
                    models.CharField(
                        max_length=256, verbose_name='Github Repository'
                    ),
                ),
                (
                    'github_user',
                    models.CharField(
                        max_length=256, verbose_name='Github Username'
                    ),
                ),
            ],
            options={'ordering': ('source', 'github_user', 'github_repo')},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AlterUniqueTogether(
            name='notificationsecret',
            unique_together={('source', 'github_user', 'github_repo')},
        ),
        migrations.AlterModelOptions(
            name='role', options={'ordering': ['namespace', 'name']}
        ),
        migrations.AlterField(
            model_name='role',
            name='is_valid',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='role',
            name='license',
            field=models.CharField(
                max_length=50, verbose_name='License (optional)', blank=True
            ),
        ),
        migrations.RemoveField(model_name='roleimport', name='role'),
        migrations.RemoveField(model_name='role', name='owner'),
        migrations.AddField(
            model_name='role',
            name='github_branch',
            field=models.CharField(
                default='',
                max_length=256,
                verbose_name='Github Branch',
                blank=True,
            ),
        ),
        migrations.DeleteModel(name='RoleImport'),
    ]
