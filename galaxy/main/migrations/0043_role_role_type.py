# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_auto_20160721_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='role_type',
            field=models.CharField(default=b'ANS', max_length=3, editable=False, choices=[(b'ANS', b'Ansible'), (b'CON', b'Container Role'), (b'APP', b'Container App')]),
        ),
    ]
