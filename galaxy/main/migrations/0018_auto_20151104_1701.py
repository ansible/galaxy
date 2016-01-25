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
                    role.namespace = role.owner.username
                    role.save()
            except:
                pass

    dependencies = [
        ('main', '0017_auto_20151104_1700'),
    ]

    operations = [
        migrations.RunPython(set_namespace),
    ]
