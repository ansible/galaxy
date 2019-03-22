from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0122_auto_20181015_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importtaskmessage',
            name='message_text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='importtaskmessage',
            name='rule_desc',
            field=models.TextField(null=True),
        ),
    ]
