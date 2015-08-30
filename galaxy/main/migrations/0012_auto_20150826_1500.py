# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def move_categories_to_tags(apps, schema_editor):
        # tags will replace categories
        Roles = apps.get_model("main", "Role")
        for role in Roles.objects.all():
            tags = []
            for category in role.categories.all():
                tags.append(category.name)
            if len(tags) > 0:
                role.tags = tags
                role.save()

    dependencies = [
        ('main', '0011_role_tags'),
    ]

    operations = [
        migrations.RunPython(move_categories_to_tags),
    ]
