# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0014_auto_20150917_1211')]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='categories',
            field=models.ManyToManyField(
                related_name='categories',
                editable=False,
                to='main.Category',
                blank=True,
                help_text='',
                verbose_name='Categories',
            ),
        ),
        migrations.AlterField(
            model_name='role',
            name='tags',
            field=models.ManyToManyField(
                related_name='roles',
                editable=False,
                to='main.Tag',
                blank=True,
                help_text='',
                verbose_name='Tags',
            ),
        ),
    ]
