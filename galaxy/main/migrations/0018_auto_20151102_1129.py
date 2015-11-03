# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, transaction


class Migration(migrations.Migration):

    @transaction.atomic
    def copy_owners_to_organizations(apps, schema_editor):
        Users = apps.get_model("accounts", "CustomUser")
        Organization = apps.get_model("main", "Organization")
        for user in Users.objects.all():
            user.organizations.create(
                name = user.username,
                description = user.username,
                active = True,
            )
    
    dependencies = [
        ('main', '0017_organization'),
    ]

    operations = [
        migrations.RunPython(copy_owners_to_organizations),
    ]
