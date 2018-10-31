# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_cloudplatform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='role_type',
            field=models.CharField(
                default='ANS', max_length=3, editable=False,
                choices=[
                    ('ANS', 'Ansible'),
                    ('CON', 'Container Enabled'),
                    ('APP', 'Container App'),
                    ('DEM', 'Demo')],
            ),
        ),
    ]
