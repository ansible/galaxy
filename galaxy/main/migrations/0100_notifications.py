from django.db import migrations, models
import django.db.models.deletion


UPGRADE_NOTIFICATIONS = """
UPDATE main_notification n SET import_task_id = (
  SELECT ni.importtask_id FROM main_notification_imports ni
  WHERE n.id = ni.notification_id
  ORDER BY ni.notification_id DESC
  LIMIT 1
), repository_id = (
  SELECT c.repository_id FROM main_notification_roles nr
  JOIN main_content c ON c.id = nr.content_id
  WHERE n.id = nr.notification_id
  LIMIT 1
);

WITH notifications_to_delete AS (
  SELECT n.id FROM main_notification n
  WHERE n.import_task_id IS NULL OR n.repository_id IS NULL
), d1 AS (
  DELETE FROM main_notification_imports
  WHERE notification_id IN (SELECT id FROM notifications_to_delete)
), d2 AS (
  DELETE FROM main_notification_roles
  WHERE notification_id IN (SELECT id FROM notifications_to_delete)
)
DELETE FROM main_notification
WHERE id IN (SELECT id FROM notifications_to_delete);
"""


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0099_namespace_vendor'),
    ]

    operations = [
        migrations.RunSQL(sql='SET CONSTRAINTS ALL IMMEDIATE'),
        migrations.AddField(
            model_name='notification',
            name='import_task',
            field=models.ForeignKey(
                null=True,
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to='main.ImportTask',
                verbose_name='Tasks'),
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
        migrations.RunSQL(sql=UPGRADE_NOTIFICATIONS),
        migrations.AlterField(
            model_name='notification',
            name='import_task',
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to='main.ImportTask',
                verbose_name='Tasks'),
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
