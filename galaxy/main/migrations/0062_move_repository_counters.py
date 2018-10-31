# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

UPGRADE_REPOSITORY_COUNTERS = """
UPDATE main_repository rp SET
  "commit"       = r."commit",
  commit_message = r.commit_message,
  commit_url     = r.commit_url,
  commit_created = r.commit_created,
  forks_count = r.forks_count,
  open_issues_count = r.open_issues_count,
  stargazers_count = r.stargazers_count,
  watchers_count = r.watchers_count
FROM main_role r
WHERE rp.id = r.repository_id;
"""

DOWNGRADE_REPOSITORY_COUNTER = """
UPDATE main_role r SET
  "commit"       = rp."commit",
  commit_message = rp.commit_message,
  commit_url     = rp.commit_url,
  commit_created = rp.commit_created,
  forks_count = rp.forks_count,
  open_issues_count = rp.open_issues_count,
  stargazers_count = rp.stargazers_count,
  watchers_count = rp.watchers_count
FROM main_repository rp
WHERE rp.id = r.repository_id
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0061_role_repo_ref'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository', name='commit',
            field=models.CharField(max_length=256, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='repository', name='commit_message',
            field=models.CharField(max_length=256, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='repository', name='commit_url',
            field=models.CharField(max_length=256, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='repository', name='commit_created',
            field=models.DateTimeField(
                null=True, verbose_name='Laste Commit DateTime'),
        ),
        migrations.AddField(
            model_name='repository', name='forks_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='repository', name='open_issues_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='repository', name='stargazers_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='repository', name='watchers_count',
            field=models.IntegerField(default=0),
        ),
        migrations.RunSQL(
            sql=UPGRADE_REPOSITORY_COUNTERS,
            reverse_sql=DOWNGRADE_REPOSITORY_COUNTER),
        migrations.RemoveField(model_name='role', name='commit'),
        migrations.RemoveField(model_name='role', name='commit_message'),
        migrations.RemoveField(model_name='role', name='commit_url'),
        migrations.RemoveField(model_name='role', name='commit_created'),
        migrations.RemoveField(model_name='role', name='forks_count'),
        migrations.RemoveField(model_name='role', name='open_issues_count'),
        migrations.RemoveField(model_name='role', name='stargazers_count'),
        migrations.RemoveField(model_name='role', name='watchers_count'),
    ]
