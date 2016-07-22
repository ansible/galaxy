# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_auto_20160207_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='readme_html',
            field=models.TextField(default=b'', verbose_name=b'README HTML', blank=True),
        ),
        migrations.AlterField(
            model_name='namespace',
            name='namespace',
            field=models.CharField(unique=True, max_length=256, verbose_name=b'GitHub namespace'),
        ),
        migrations.AlterField(
            model_name='role',
            name='readme',
            field=models.TextField(default=b'', verbose_name=b'README raw content', blank=True),
        ),
    ]
