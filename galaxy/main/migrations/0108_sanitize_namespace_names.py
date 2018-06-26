# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-31 13:18
from __future__ import unicode_literals

from django.db import migrations, models
import galaxy.main.fields

STRIP_VERSION_SUFFIX = """
UPDATE main_namespace
SET name = replace(name, '-', '_')
WHERE name LIKE '%-%'
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0107_cloud_platforms'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(STRIP_VERSION_SUFFIX),
        ),
    ]
