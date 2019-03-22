from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0110_revert_sanitize_namespace_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='deprecated',
            field=models.BooleanField(default=False),
        ),
    ]
