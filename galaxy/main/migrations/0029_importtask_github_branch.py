# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [('main', '0028_auto_20151125_1231')]

    operations = [
        migrations.AddField(
            model_name='importtask',
            name='github_branch',
            field=models.CharField(
                default='',
                max_length=256,
                verbose_name='Github Branch',
                blank=True,
            ),
        )
    ]
