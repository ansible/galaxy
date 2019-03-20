# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations, IntegrityError

import galaxy.main.fields
import galaxy.main.mixins


def copy_categories_to_tags(apps, schema_editor):
    # tags will replace categories
    db_alias = schema_editor.connection.alias
    Categories = apps.get_model("main", "Category")
    Tag = apps.get_model("main", "Tag")
    for category in Categories.objects.using(db_alias).all():
        for name in category.name.split(':'):
            tag = Tag(name=name, description=name, active=True)
            try:
                tag.save(using=db_alias)
            except IntegrityError:
                pass


def copy_tags(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Roles = apps.get_model("main", "Role")
    Tags = apps.get_model("main", "Tag")
    for role in Roles.objects.using(db_alias).all():
        for category in role.categories.all():
            for name in category.name.split(':'):
                if not role.tags.filter(name=name).exists():
                    t = Tags.objects.using(db_alias).get(name=name)
                    role.tags.add(t)
                    role.save()


class Migration(migrations.Migration):

    dependencies = [('main', '0010_auto_20150826_1017')]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID',
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    'description',
                    galaxy.main.fields.TruncatingCharField(
                        default='', max_length=255, blank=True
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                (
                    'name',
                    models.CharField(
                        unique=True, max_length=512, db_index=True
                    ),
                ),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={'ordering': ['name'], 'verbose_name_plural': 'Tags'},
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AddField(
            model_name='role',
            name='tags',
            field=models.ManyToManyField(
                related_name='tags',
                verbose_name='Tags',
                editable=False,
                to='main.Tag',
                blank=True,
            ),
        ),
        migrations.RunPython(copy_categories_to_tags),
        migrations.RunPython(copy_tags),
    ]
