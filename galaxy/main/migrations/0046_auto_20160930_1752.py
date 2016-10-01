# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_role_commit_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='min_ansible_container_version',
            field=models.CharField(max_length=10, null=True, verbose_name=b'Min Ansible Container Version', blank=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='min_ansible_version',
            field=models.CharField(max_length=10, null=True, verbose_name=b'Min Ansible Version', blank=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='role_type',
            field=models.CharField(default=b'ANS', max_length=3, editable=False, choices=[(b'ANS', b'Ansible'), (b'CON', b'Container Enabled'), (b'APP', b'Container App')]),
        ),
    ]
