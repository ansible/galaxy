# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20150824_1444'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='platform',
            index_together=set([('id', 'name')]),
        ),
    ]
