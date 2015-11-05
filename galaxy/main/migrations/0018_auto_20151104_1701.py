# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, transaction
from django.db.models import Count

class Migration(migrations.Migration):

    @transaction.atomic
    def set_namespace(apps, schema_editor):
        Roles = apps.get_model("main", "Role")
        for role in Roles.objects.all().order_by('github_user','name','-modified'):
            try:
                with transaction.atomic():
                    role.namespace = role.github_user
                    role.save()
            except:
                pass

    @transaction.atomic
    def remove_duplicates(apps, schema_editor):
         Roles = apps.get_model("main", "Role")
         for role in Roles.objects.filter(namespace=None):
            role.delete()

    dependencies = [
        ('main', '0017_auto_20151104_1700'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('namespace', 'name')]),
        ),
        migrations.RunPython(set_namespace),
        migrations.RunPython(remove_duplicates),  
    ]
