# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20151117_0646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='github_branch',
            field=models.CharField(verbose_name=b'GitHub Branch', max_length=256, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='imports',
            field=models.ManyToManyField(verbose_name=b'Tasks', editable=False, to='main.ImportTask', related_name='notifications'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='messages',
            field=django.contrib.postgres.fields.ArrayField(default=list, base_field=models.CharField(max_length=256), editable=False, size=None),
        ),
        migrations.AlterField(
            model_name='notification',
            name='owner',
            field=models.ForeignKey(related_name='notifications', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notification',
            name='roles',
            field=models.ManyToManyField(verbose_name=b'Roles', editable=False, to='main.Role', related_name='notifications'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='source',
            field=models.CharField(verbose_name=b'Source', max_length=20, editable=False),
        ),
    ]
