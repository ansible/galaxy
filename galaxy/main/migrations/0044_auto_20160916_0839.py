# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0043_role_role_type')]

    operations = [
        migrations.AddField(
            model_name='role',
            name='container_yml',
            field=models.TextField(
                null=True, verbose_name='container.yml', blank=True
            ),
        )
    ]
