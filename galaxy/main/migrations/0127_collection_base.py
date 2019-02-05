from django.db import migrations, models
import django.db.models.deletion


def create_galaxy_repository(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Repository = apps.get_model("pulp_app", "Repository")
    Repository.objects.using(db_alias).create(name="galaxy")


def delete_galaxy_repository(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Repository = apps.get_model("pulp_app", "Repository")
    obj = Repository.objects.using(db_alias).filter(name="galaxy").first()
    if obj:
        obj.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('pulp_app', '0001_initial'),
        ('main', '0126_notification_commit_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('namespace', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('_content', models.OneToOneField(
                    db_column='id',
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    related_name='+',
                    serialize=False,
                    to='pulp_app.Content')),
            ],
            bases=('pulp_app.content',),
        ),
        migrations.CreateModel(
            name='CollectionVersion',
            fields=[
                ('version', models.CharField(max_length=32)),
                ('_content', models.OneToOneField(
                    db_column='id',
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    related_name='+',
                    serialize=False,
                    to='pulp_app.Content')),
                ('collection',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='versions',
                     to='main.Collection')),
            ],
            bases=('pulp_app.content',),
        ),
        migrations.AlterUniqueTogether(
            name='collection',
            unique_together={('namespace', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='collectionversion',
            unique_together={('version', 'collection')},
        ),
        migrations.RunPython(
            code=create_galaxy_repository,
            reverse_code=delete_galaxy_repository)
    ]
