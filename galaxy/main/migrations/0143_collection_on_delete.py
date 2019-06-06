from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0142_collection_search'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='latest_version',
            field=models.ForeignKey(
                null=True,
                on_delete=models.SET_NULL,
                related_name='+',
                to='main.CollectionVersion'),
        ),
        migrations.AlterField(
            model_name='collectionversion',
            name='collection',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='versions',
                to='main.Collection'),
        ),
    ]
