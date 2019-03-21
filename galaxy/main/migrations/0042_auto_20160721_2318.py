# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0041_auto_20160207_2148')]

    operations = [
        migrations.AddField(
            model_name='role',
            name='readme_html',
            field=models.TextField(
                default='', verbose_name='README HTML', blank=True
            ),
        ),
        migrations.AlterField(
            model_name='namespace',
            name='namespace',
            field=models.CharField(
                unique=True, max_length=256, verbose_name='GitHub namespace'
            ),
        ),
        migrations.AlterField(
            model_name='role',
            name='readme',
            field=models.TextField(
                default='', verbose_name='README raw content', blank=True
            ),
        ),
    ]
