# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, IntegrityError, transaction

import galaxy.main.fields
import galaxy.main.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20150826_1017'),
    ]

    @transaction.atomic
    def copy_categories_to_tags(apps, schema_editor):
        # tags will replace categories
        Categories = apps.get_model("main", "Category")
        Tag = apps.get_model("main", "Tag")
        for category in Categories.objects.all():
            for name in category.name.split(':'):
                try:
                    with transaction.atomic():
                        tag = Tag(
                            name=name,
                            description=name,
                            active=True
                        )
                        tag.save()
                except IntegrityError:
                    pass

    @transaction.atomic
    def copy_tags(apps, schema_editor):
        Roles = apps.get_model("main", "Role")
        Tags = apps.get_model("main", "Tag")
        for role in Roles.objects.all():
            for category in role.categories.all():
                for name in category.name.split(':'):
                    if not role.tags.filter(name=name).exists():
                        t = Tags.objects.get(name=name)
                        role.tags.add(t)
                        role.save()

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', galaxy.main.fields.TruncatingCharField(default=b'', max_length=255, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(unique=True, max_length=512, db_index=True)),
                ('original_name', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Tags',
            },
            bases=(models.Model, galaxy.main.mixins.DirtyMixin),
        ),
        migrations.AddField(
            model_name='role',
            name='tags',
            field=models.ManyToManyField(related_name='tags', verbose_name=b'Tags', editable=False, to='main.Tag', blank=True),
        ),
        migrations.RunPython(copy_categories_to_tags),
        migrations.RunPython(copy_tags),
    ]
