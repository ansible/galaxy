from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0098_readme'),
    ]

    operations = [
        migrations.AddField(
            model_name='namespace',
            name='is_vendor',
            field=models.BooleanField(default=False),
        ),
    ]
