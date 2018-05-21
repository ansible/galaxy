from __future__ import unicode_literals

import logging

from django.db import migrations
from django.db import models


LOG = logging.getLogger(__name__)


def delete_empty_repositories(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Repository = apps.get_model('main', 'Repository')

    qs = (
        Repository.objects.using(db_alias)
        .annotate(content_count=models.Count('content_objects'))
        .filter(content_count=0)
    )

    count = qs.count()
    LOG.info('Deleting {0} Repository records'.format(count))

    for repo in qs:
        repo.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0096_repository_format'),
    ]

    operations = [
        migrations.RunPython(code=delete_empty_repositories,
                             reverse_code=migrations.RunPython.noop)
    ]
