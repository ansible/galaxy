from __future__ import unicode_literals

import hashlib

from django.db import migrations
from django.db import models

import galaxy.main.mixins


DROP_SEARCH_VECTOR_UPDATE_TRIGGER = """
DROP TRIGGER update_content_search_vector_trigger ON main_content;
DROP FUNCTION update_content_search_vector();
"""

CREATE_SEARCH_VECTOR_UPDATE_FUNCTIONS = """
CREATE OR REPLACE FUNCTION on_content_update_search_vector_trigger()
RETURNS TRIGGER AS $$
DECLARE readme_raw TEXT;
BEGIN
  SELECT raw INTO readme_raw FROM main_readme WHERE id = NEW.readme_id;
  NEW.search_vector :=
    setweight(to_tsvector(NEW.name), 'A')
    || setweight(to_tsvector(NEW.description), 'C')
    || setweight(to_tsvector(COALESCE(readme_raw, '')), 'D');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_search_vector
BEFORE INSERT OR UPDATE ON main_content
FOR EACH ROW EXECUTE PROCEDURE on_content_update_search_vector_trigger();
"""


def copy_readme_to_separate_table(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    Content = apps.get_model("main", "Content")
    Readme = apps.get_model("main", "Readme")

    # NOTE(cutwater): This query will not include readme objects that
    # have text but no type.
    contents = Content.objects.using(db_alias).filter(
        readme_raw__isnull=False, readme_type__isnull=False
    )
    for content_obj in contents:
        if content_obj.readme_type == 'md':
            mimetype = 'text/markdown'
        elif content_obj.readme_type == 'rst':
            mimetype = 'text/x-rst'
        else:
            raise ValueError(
                'Unexpected readme_type value: "{0}"'.format(
                    content_obj.readme_type
                )
            )

        readme_bytes = content_obj.readme_raw.encode('utf-8')
        readme_hash = hashlib.sha256(readme_bytes).hexdigest()

        readme_obj, _ = Readme.objects.using(db_alias).get_or_create(
            repository=content_obj.repository,
            raw_hash=readme_hash,
            defaults={
                'raw': readme_bytes,
                'html': content_obj.readme_html,
                'mimetype': mimetype,
            },
        )
        content_obj.readme = readme_obj
        content_obj.save()


class Migration(migrations.Migration):
    dependencies = [('main', '0097_delete_empty_repos')]

    operations = [
        migrations.RunSQL(DROP_SEARCH_VECTOR_UPDATE_TRIGGER),
        migrations.RenameField(
            model_name='content', old_name='readme', new_name='readme_raw'
        ),
        migrations.CreateModel(
            name='Readme',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('raw', models.TextField()),
                ('raw_hash', models.CharField(max_length=128)),
                ('mimetype', models.CharField(max_length=32)),
                ('html', models.TextField()),
                (
                    'repository',
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name='+',
                        to='main.Repository',
                    ),
                ),
            ],
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AlterUniqueTogether(
            name='readme', unique_together={('repository', 'raw_hash')}
        ),
        migrations.AddField(
            model_name='content',
            name='readme',
            field=models.ForeignKey(
                null=True,
                on_delete=models.PROTECT,
                related_name='+',
                to='main.Readme',
            ),
        ),
        migrations.AddField(
            model_name='repository',
            name='readme',
            field=models.ForeignKey(
                null=True,
                on_delete=models.PROTECT,
                related_name='+',
                to='main.Readme',
            ),
        ),
        migrations.RunSQL(CREATE_SEARCH_VECTOR_UPDATE_FUNCTIONS),
        migrations.RunPython(copy_readme_to_separate_table),
        migrations.RemoveField(model_name='content', name='readme_raw'),
        migrations.RemoveField(model_name='content', name='readme_html'),
        migrations.RemoveField(model_name='content', name='readme_type'),
    ]
