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
                default=b'ANS', max_length=3, editable=False,
                choices=[
                    (b'ANS', b'Ansible'),
                    (b'CON', b'Container Enabled'),
                    (b'APP', b'Container App'),
                    (b'DEM', b'Demo')],
            ),
        ),
    ]
