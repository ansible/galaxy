# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_role_role_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='container_yml',
            field=models.TextField(null=True, verbose_name=b'container.yml', blank=True),
        )
    ]
