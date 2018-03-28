# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import galaxy.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0080_auto_20180212_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='metadata',
            field=galaxy.main.fields.JSONField(default={}),
        ),
    ]
