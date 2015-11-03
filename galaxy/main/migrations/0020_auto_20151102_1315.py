# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_role_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='organization',
            field=models.ForeignKey(related_name='roles', editable=False, to='main.Organization'),
        ),
    ]
