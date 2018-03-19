# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0077_auto_20180201_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importtaskmessage',
            name='message_type',
            field=models.CharField(max_length=10, choices=[
                ('DEBUG', 'DEBUG'),
                ('ERROR', 'ERROR'),
                ('FAILED', 'FAILED'),
                ('INFO', 'INFO'),
                ('SUCCESS', 'SUCCESS'),
                ('WARNING', 'WARNING')]),
        ),
        migrations.AlterField(
            model_name='providernamespace',
            name='avatar_url',
            field=models.CharField(max_length=256, null=True,
                                   verbose_name=b'Avatar URL', blank=True),
        ),
        migrations.AlterField(
            model_name='providernamespace',
            name='company',
            field=models.CharField(max_length=256, null=True,
                                   verbose_name=b'Company Name', blank=True),
        ),
        migrations.AlterField(
            model_name='providernamespace',
            name='email',
            field=models.CharField(max_length=256, null=True,
                                   verbose_name=b'Email Address', blank=True),
        ),
        migrations.AlterField(
            model_name='providernamespace',
            name='followers',
            field=models.IntegerField(null=True, verbose_name=b'Followers'),
        ),
        migrations.AlterField(
            model_name='providernamespace',
            name='html_url',
            field=models.CharField(max_length=256, null=True,
                                   verbose_name=b'Web Site URL', blank=True),
        ),
        migrations.AlterField(
            model_name='providernamespace',
            name='location',
            field=models.CharField(max_length=256, null=True,
                                   verbose_name=b'Location', blank=True),
        ),
    ]
