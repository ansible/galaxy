# NOTE(cutwater): This migration is replaced by v2_4_0 and should be
#   deleted once superseding migration is merged into master.
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20151118_1425'),
    ]

    operations = [
        migrations.RenameField(
            model_name='role',
            old_name='open_issue_count',
            new_name='open_issues_count',
        ),
    ]
