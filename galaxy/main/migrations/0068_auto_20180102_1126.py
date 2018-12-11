# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0067_bind_stargazers_to_repo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='providernamespace',
            name='namespace',
            field=models.ForeignKey(
                related_name='provider_namespaces',
                editable=False, to='main.Namespace',
                null=True, on_delete=models.CASCADE,
                verbose_name='Namespace'
            ),
        ),
        migrations.AlterField(
            model_name='providernamespace',
            name='provider',
            field=models.ForeignKey(
                related_name='provider_namespaces',
                verbose_name='Provider',
                to='main.Provider', null=True,
                on_delete=models.CASCADE,
            ),
        ),
    ]
