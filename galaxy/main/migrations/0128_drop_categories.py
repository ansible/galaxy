from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0127_collection_base'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='categories',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
