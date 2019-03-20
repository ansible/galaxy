# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_stargazer_role_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stargazer',
            name='role',
            field=models.ForeignKey(
                related_name='stars',
                to='main.Role',
                on_delete=models.CASCADE,
            ),
        ),
    ]
