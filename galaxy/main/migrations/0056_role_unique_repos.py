# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import migrations


ROLE_DUPLICATES_QUERY = """
SELECT id FROM (
  SELECT
    id, ROW_NUMBER() OVER (
      PARTITION BY github_user, github_repo
      ORDER BY modified DESC) AS rnum
  FROM main_role) temp
WHERE temp.rnum > 1;
"""


def drop_role_duplicates(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Role = apps.get_model('main', 'Role')
    # NOTE(cutwater): All on_delete constraints in Django are software
    # defined, so we have to first query ids for deletion and then delete
    # Role objects with ORM.
    roles = Role.objects.using(db_alias).raw(ROLE_DUPLICATES_QUERY)
    for role in (
            Role.objects.using(db_alias)
            .filter(pk__in=(r.id for r in roles))):
        # NOTE(cutwater): When calling .delete() on QuerySet, Django ORM
        # it seems that on_delete is not executed, so we have to execute
        # .delete() on each object specifically.
        role.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0055_contentblock'),
    ]

    operations = [
        # NOTE(cutwater): Since Django creates all constraints as DEFERRED,
        # we need to set them to IMMEDIATE to perform DDL and DML queries
        # in one single transaction.
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE',
                          reverse_sql=migrations.RunSQL.noop),
        migrations.RunPython(drop_role_duplicates,
                             reverse_code=migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={
                ('namespace', 'name'),
                ('github_user', 'github_repo')
            },
        ),
        migrations.RunSQL(sql=migrations.RunSQL.noop,
                          reverse_sql='SET CONSTRAINTS ALL IMMEDIATE'),
    ]
