from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def upgrade_data(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Notification = apps.get_model("main", "Notification")
    for notification in Notification.objects.using(db_alias).all():
        import_task = notification.imports.order_by('-id').first()
        content = notification.roles.first()

        if import_task and content:
            notification.import_task = import_task
            notification.repository = content.repository
            notification.save()
        else:
            notification.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0099_namespace_vendor'),
    ]

    operations = [
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE',
                          reverse_sql=migrations.RunSQL.noop),
        migrations.AddField(
            model_name='notification',
            name='import_task',
            field=models.ForeignKey(
                null=True,
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to='main.ImportTask',
                verbose_name=b'Tasks'),
        ),
        migrations.AddField(
            model_name='notification',
            name='repository',
            field=models.ForeignKey(
                null=True,
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to='main.Repository'),
        ),
        migrations.RunPython(code=upgrade_data),
        migrations.AlterField(
            model_name='notification',
            name='import_task',
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to='main.ImportTask',
                verbose_name=b'Tasks'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='repository',
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to='main.Repository'),
        ),
        migrations.RemoveField(
            model_name='notification',
            name='imports',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='messages',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='roles',
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('provider_namespace', 'original_name'),
                             ('provider_namespace', 'name')},
        ),
    ]
