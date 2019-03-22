from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE accounts_customuser "
            "ALTER COLUMN last_login DROP NOT NULL;"
        )
    ]
