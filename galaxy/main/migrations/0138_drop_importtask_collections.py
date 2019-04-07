from django.db import migrations
from django.db import models


# noinspection PyPep8Naming
def drop_collection_import_tasks(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ImportTask = apps.get_model('main', 'ImportTask')
    ImportTask.objects.using(db_alias).filter(repository__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0137_collectionimport_imported_version'),
    ]

    operations = [
        migrations.RunPython(
            code=drop_collection_import_tasks,
            reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='importtask',
            name='collection',
        ),
        migrations.AlterField(
            model_name='importtask',
            name='repository',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='import_tasks',
                to='main.Repository'),
        ),
    ]
