# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.postgres import fields as psql_fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0080_auto_20180212_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='metadata',
            field=psql_fields.JSONField(default={}),
        ),
    ]
