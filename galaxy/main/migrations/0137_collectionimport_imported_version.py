from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0136_collection_survey_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionimport',
            name='imported_version',
            field=models.ForeignKey(
                to='main.CollectionVersion',
                null=True,
                on_delete=models.SET_NULL,
                related_name='import_tasks'),
        ),
    ]
