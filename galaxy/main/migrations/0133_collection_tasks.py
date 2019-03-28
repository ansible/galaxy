from django.contrib.postgres import fields as psql_fields
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ('pulp_app', '0002_task_name'),
        ('main', '0132_update_collecion_scores'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('params', psql_fields.JSONField(null=True)),
                ('result', psql_fields.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CollectionImport',
            fields=[
                ('task_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=models.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='main.Task')),
                ('name', models.CharField(max_length=64)),
                ('version', models.CharField(max_length=64)),
                ('messages', psql_fields.JSONField(default=list)),
                ('lint_records', psql_fields.JSONField(default=list)),
                ('namespace', models.ForeignKey(
                     on_delete=models.CASCADE,
                     to='main.Namespace')),
            ],
            bases=('main.task',),
        ),
        migrations.AddField(
            model_name='task',
            name='pulp_task',
            field=models.OneToOneField(
                on_delete=models.CASCADE,
                related_name='galaxy_task',
                to='pulp_app.Task'),
        ),
    ]
