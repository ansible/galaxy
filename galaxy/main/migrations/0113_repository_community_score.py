from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0112_auto_20180817_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='community_score',
            field=models.FloatField(null=True),
        ),
    ]
