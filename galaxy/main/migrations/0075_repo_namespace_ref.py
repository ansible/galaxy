from django.db import models, migrations


UPGRADE_SET_REPO_NAMESPACE_REF = """
UPDATE main_repository r
SET provider_namespace_id = pn.id
FROM main_providernamespace pn
WHERE r.github_user = pn.name
"""

SELECT_DUPLICATE_REPOS = """
SELECT
    provider_namespace_id,
    name
FROM main_repository
GROUP BY provider_namespace_id, name
HAVING count(*) > 1
"""

SELECT_INVALID_CONTENT = """
SELECT c.id
FROM main_repository r
JOIN main_content c
    ON r.id = c.repository_id
WHERE
    (r.provider_namespace_id, r.name) IN ({0}) AND c.is_valid = FALSE

""".format(SELECT_DUPLICATE_REPOS)

SELECT_INVALID_REPOS = """
SELECT r.id
FROM main_repository r
LEFT JOIN main_content c
    ON r.id = c.repository_id
WHERE
    (r.provider_namespace_id, r.name) IN ({0})
    AND (c.id IS NULL OR c.is_valid = FALSE)
""".format(SELECT_DUPLICATE_REPOS)


def delete_duplicate_repos(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Repository = apps.get_model("main", "Repository")
    Content = apps.get_model("main", "Content")
    for content in Content.objects.using(db_alias).raw(SELECT_INVALID_CONTENT):
        content.delete()
    for repo in Repository.objects.using(db_alias).raw(SELECT_INVALID_REPOS):
        repo.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0074_repo_import_branch'),
    ]

    operations = [
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE',
                          reverse_sql=migrations.RunSQL.noop),
        migrations.AddField(
            model_name='repository',
            name='provider_namespace',
            field=models.ForeignKey(
                to='main.ProviderNamespace',
                null=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.RunSQL(sql=UPGRADE_SET_REPO_NAMESPACE_REF,
                          reverse_sql=migrations.RunSQL.noop),
        migrations.RunPython(code=delete_duplicate_repos,
                             reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='repository',
            name='provider_namespace',
            field=models.ForeignKey(
                related_name='repositories',
                to='main.ProviderNamespace',
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('provider_namespace', 'name')},
        ),
        migrations.AlterModelOptions(
            name='repository',
            options={'ordering': ('provider_namespace', 'name')},
        ),
        migrations.RemoveField(
            model_name='repository',
            name='github_user'
        ),
    ]
