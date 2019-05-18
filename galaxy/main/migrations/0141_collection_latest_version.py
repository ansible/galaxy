from django.db import migrations
from django.db import models
import semantic_version as semver


def _find_latest_version(collection):
    versions = collection.versions.all()
    if not versions:
        return None
    d = {semver.Version(v.version): v for v in versions}
    highest = semver.Spec('*').select(d.keys())
    return d[highest]


def update_latest_version(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Collection = apps.get_model('main', 'Collection')
    for collection in Collection.objects.using(db_alias).all():
        collection.latest_version = _find_latest_version(collection)
        collection.save()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0140_usernotification_collection'),
    ]

    operations = [
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE',
                          reverse_sql=migrations.RunSQL.noop),
        migrations.AddField(
            model_name='collection',
            name='latest_version',
            field=models.ForeignKey(
                to='main.CollectionVersion',
                on_delete=models.PROTECT,
                null=True,
                related_name='+',
            ),
        ),
        migrations.RunPython(
            code=update_latest_version,
            reverse_code=migrations.RunPython.noop),
    ]
