from __future__ import unicode_literals
import logging

from django.db import migrations


LOG = logging.getLogger(__package__)


def delete_contents_invalid_name(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Content = apps.get_model('main', 'Content')

    qs = Content.objects.using(db_alias).exclude(name__iregex='^[\w-]+$')

    count = qs.count()
    LOG.info('Deleting {0} Content records'.format(count))

    for content in qs:
        content.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0088_auto_20180328_1209'),
    ]

    operations = [
        migrations.RunPython(
            code=delete_contents_invalid_name,
            reverse_code=migrations.RunPython.noop,
        )
    ]
