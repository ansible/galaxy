from django.contrib.postgres import indexes as psql_indexes
from django.contrib.postgres import fields as psql_fields
from django.contrib.postgres import search as psql_search
from django.db import migrations
from django.db import models


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
        ('main', '0127_drop_categories'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('deprecated', models.BooleanField(default=False)),
                ('download_count', models.IntegerField(default=0.0)),
                ('community_score', models.FloatField(default=0.0)),
                ('quality_score', models.FloatField(default=0.0)),
                ('search_vector', psql_search.SearchVectorField(default='')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('namespace', models.ForeignKey(
                    on_delete=models.PROTECT,
                    to='main.Namespace')),
                ('tags', models.ManyToManyField(to='main.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='CollectionVersion',
            fields=[
                ('version', models.CharField(max_length=64)),
                ('hidden', models.BooleanField(default=False)),
                ('metadata', psql_fields.JSONField(default=dict)),
                ('contents', psql_fields.JSONField(default=dict)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('_content', models.OneToOneField(
                    db_column='id',
                    on_delete=models.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    related_name='+',
                    serialize=False,
                    to='pulp_app.Content')),
                ('collection', models.ForeignKey(
                    on_delete=models.PROTECT,
                    related_name='versions',
                    to='main.Collection')),
            ],
            bases=('pulp_app.content',),
        ),
        migrations.AlterUniqueTogether(
            name='collectionversion',
            unique_together={('collection', 'version')},
        ),
        migrations.AlterUniqueTogether(
            name='collection',
            unique_together={('namespace', 'name')},
        ),
        migrations.AddIndex(
            model_name='collection',
            index=psql_indexes.GinIndex(
                fields=['search_vector'],
                name='main_collec_search__7ca832_gin'),
        ),
        migrations.RunPython(
            code=create_galaxy_repository,
            reverse_code=delete_galaxy_repository)
    ]
