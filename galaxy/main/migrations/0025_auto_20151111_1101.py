# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20151110_0612'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='importtask',
            options={'ordering': ('-id',)},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['namespace', 'name']},
        ),
        migrations.AddField(
            model_name='importtask',
            name='github_reference',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Github Reference', blank=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='license',
            field=models.CharField(max_length=50, verbose_name=b'License (optional)', blank=True),
        ),
    ]
