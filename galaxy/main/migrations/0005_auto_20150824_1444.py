# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from galaxy.api.aggregators import *


def update_roles(apps, schema_editor):
    # Going forward num_ratings and average_score will be stored on the role
    Roles = apps.get_model("main", "Role")
    for role in Roles.objects.all():
        role.num_ratings = role.ratings.filter(active=True).count()
        role.average_score = role.ratings.filter(active=True).aggregate(
            avg=AvgWithZeroForNull('score'))['avg'] or 0
        role.save()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0004_auto_20150824_1430'),
    ]

    operations = [
        migrations.RunPython(update_roles)
    ]
