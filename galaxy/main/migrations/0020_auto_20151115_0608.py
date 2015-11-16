# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20151113_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='source',
            field=models.CharField(max_length=20, verbose_name=b'Source'),
        ),
        migrations.AlterModelOptions(
            name='notificationsecret',
            options={'ordering': ('source', 'github_user', 'github_repo')},
        ),
        migrations.AlterUniqueTogether(
            name='notificationsecret',
            unique_together=set([('source', 'github_user', 'github_repo')]),
        ),
        migrations.AlterField(
            model_name='notificationsecret',
            name='github_repo',
            field=models.CharField(max_length=256, verbose_name=b'Github Repository'),
        ),
        migrations.AlterField(
            model_name='notificationsecret',
            name='github_user',
            field=models.CharField(max_length=256, verbose_name=b'Github Username'),
        ),
        migrations.AlterField(
            model_name='notificationsecret',
            name='secret',
            field=models.CharField(max_length=256, verbose_name=b'Secret', db_index=True),
        ),
        migrations.AlterField(
            model_name='notificationsecret',
            name='source',
            field=models.CharField(max_length=20, verbose_name=b'Source'),
        ),
    ]
