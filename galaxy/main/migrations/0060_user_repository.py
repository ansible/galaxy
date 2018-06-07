# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


UPGRADE_USER_REPOSITORY_DATA = """
INSERT INTO main_repository_owners (
  repository_id, customuser_id)
SELECT
  r2.id,
  r1.owner_id
FROM main_repository r1
JOIN (
  SELECT DISTINCT ON (github_user, github_repo)
    id, github_user, github_repo, created, modified
  FROM main_repository
  ORDER BY github_user, github_repo, owner_id
) r2
  ON r1.github_user = r2.github_user
  AND r1.github_repo = r2.github_repo
"""

UPGRADE_REMOVE_REDUNDANT_REPOSITORIES = """
DELETE FROM main_repository
WHERE id NOT IN (
  SELECT repository_id FROM main_repository_owners
)
"""

DOWNGRADE_UPDATE_REPOSITORIES = """
UPDATE main_repository r SET (owner_id) = (
  SELECT DISTINCT ON (repository_id) customuser_id
  FROM main_repository_owners ur
  WHERE r.id = ur.repository_id
  ORDER BY repository_id, customuser_id
);
"""

DOWNGRADE_INSERT_MISSING_REPOSITORIES = """
INSERT INTO main_repository (
  github_user, github_repo, owner_id, is_enabled,
  created, modified, description, active)
SELECT
  r.github_user, r.github_repo, ur.customuser_id, r.is_enabled,
    now(), now(), '', TRUE
  FROM main_repository r
  JOIN main_repository_owners ur
    ON r.id = ur.repository_id
    AND r.owner_id != ur.customuser_id;
"""


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0059_drop_role_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='owners',
            field=models.ManyToManyField(
                related_name='repositories',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='repository',
            name='owner',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, null=True, default=None),
        ),
        migrations.RunSQL(
            sql=(UPGRADE_USER_REPOSITORY_DATA,
                 UPGRADE_REMOVE_REDUNDANT_REPOSITORIES),
            reverse_sql=(DOWNGRADE_UPDATE_REPOSITORIES,
                         DOWNGRADE_INSERT_MISSING_REPOSITORIES)),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('github_user', 'github_repo')},
        ),
        migrations.RemoveField(model_name='repository', name='owner'),
        migrations.RemoveField(model_name='repository', name='active'),
        migrations.RemoveField(model_name='repository', name='description'),
    ]
