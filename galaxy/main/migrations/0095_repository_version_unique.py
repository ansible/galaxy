from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0094_import_branch'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='repositoryversion',
            unique_together={('name', 'repository')},
        ),
    ]
