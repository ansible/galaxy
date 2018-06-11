from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0105_content_block_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='readme',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+', to='main.Readme'),
        ),
        migrations.AlterField(
            model_name='repository',
            name='readme',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+', to='main.Readme'),
        ),
    ]
