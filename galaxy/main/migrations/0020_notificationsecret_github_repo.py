# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20151113_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationsecret',
            name='github_repo',
            field=models.CharField(max_length=256),
            preserve_default=False,
        ),
    ]
