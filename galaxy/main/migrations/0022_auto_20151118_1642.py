# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


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
