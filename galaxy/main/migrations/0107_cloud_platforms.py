# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


CLOUDS = [
    {
        'name': 'google',
        'description': 'Google Cloud'
    }, {
        'name': 'amazon',
        'description': 'Amazon Web Services'
    }, {
        'name': 'azure',
        'description': 'Microsoft Azure'
    }, {
        'name': 'rackspace',
        'description': 'Rackspace'
    }, {
        'name': 'centurylink',
        'description': 'CenturyLink'
    }, {
        'name': 'openstack',
        'description': 'OpenStack'
    }, {
        'name': 'ovirt',
        'description': 'oVirt'
    }, {
        'name': 'vmware',
        'description': 'VMware'
    }
]


def create_clouds(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    CloudPlatform = apps.get_model('main', 'CloudPlatform')

    for cloud in CLOUDS:
        CloudPlatform.objects.using(db_alias).create(
            name=cloud['name'], description=cloud['description'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0106_readme_on_delete'),
    ]

    operations = [
        migrations.RunPython(code=create_clouds,
                             reverse_code=migrations.RunPython.noop,),
    ]
