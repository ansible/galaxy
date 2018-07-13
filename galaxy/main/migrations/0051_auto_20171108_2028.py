# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0050_auto_20171024_0354')]

    operations = [
        migrations.RemoveField(model_name='role', name='videos'),
        migrations.AddField(
            model_name='video',
            name='role',
            field=models.ForeignKey(
                related_name='videos', to='main.Role', help_text=b'', null=True
            ),
        ),
        migrations.AlterField(
            model_name='video',
            name='url',
            field=models.CharField(help_text=b'', unique=True, max_length=256),
        ),
    ]
