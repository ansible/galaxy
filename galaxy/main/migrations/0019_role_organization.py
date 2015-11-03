# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, transaction


class Migration(migrations.Migration):
    
    @transaction.atomic
    def set_role_organization(apps, schema_editor):
        Roles = apps.get_model("main","Role")
        Users = apps.get_model("accounts","CustomUser")
        Organizations = apps.get_model("main","Organization")
        for role in Roles.objects.all():
            user = Users.objects.get(id=role.owner_id)
            org = Organizations.objects.filter(name=user.username)[0]
            org.roles.add(role)

    dependencies = [
        ('main', '0018_auto_20151102_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='organization',
            field=models.ForeignKey(related_name='roles', editable=False, to='main.Organization', null=True),
        ),
        migrations.RunPython(set_role_organization),
    ]
