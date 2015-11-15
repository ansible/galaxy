# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_notificationsecret_github_repo'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationsecret',
            name='github_user',
            field=models.CharField(max_length=256, verbose_name=b'Github Username'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notification',
            name='source',
            field=models.CharField(max_length=20, verbose_name=b'Source'),
        ),
        migrations.AlterField(
            model_name='notificationsecret',
            name='github_repo',
            field=models.CharField(max_length=256, verbose_name=b'Github Repository'),
        ),
        migrations.AlterField(
            model_name='notificationsecret',
            name='secret',
            field=models.CharField(max_length=256, verbose_name=b'Secret'),
        ),
        migrations.AlterField(
            model_name='notificationsecret',
            name='source',
            field=models.CharField(max_length=20, verbose_name=b'Source'),
        ),
    ]
