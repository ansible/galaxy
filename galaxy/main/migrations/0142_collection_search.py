from django.contrib.postgres import fields as psql_fields
from django.db import migrations

# This query generates full text search index based
# the following data ranked from A to D:
#   - Namespace name (weight A
#   - Collection name (weight A)
#   - Collection tags (weight B)
#   - Collection content names (weight C)
#   - Collection description (weight D)
TS_VECTOR_SELECT = '''
    setweight(to_tsvector(coalesce(cv.metadata ->> 'namespace', '')), 'A')
    || setweight(to_tsvector(coalesce(cv.metadata ->> 'name', '')), 'A')
    || (
      SELECT
        setweight(to_tsvector(
          coalesce(string_agg(cvt, ' '), '')
        ), 'B')
      FROM jsonb_array_elements_text(cv.metadata -> 'tags') cvt
    )
    || (
      SELECT
        setweight(to_tsvector(
          coalesce(string_agg(cvc ->> 'name', ' '), '')
        ), 'C')
      FROM jsonb_array_elements(cv.contents) AS cvc
    )
    || setweight(to_tsvector(
         coalesce(cv.metadata ->> 'description', '')
       ), 'D')
'''

# Generates search vector for existing collections in the database.
POPULATE_COLLECTIONS_TS_VECTOR = f'''
UPDATE main_collection AS c
SET search_vector = (
    SELECT {TS_VECTOR_SELECT}
    FROM main_collectionversion cv
    WHERE cv.id = c.latest_version_id
)
WHERE c.latest_version_id IS NOT NULL
'''

# Creates a database function and a trigger to update collection search
# vector field when a collection reference to a newer version is updated.
#
# Since it's not possible to insert a collection version
# before a collection, a latest_version_id always gets updated as a separated
# query after both collection and collection version are inserted.
# Thus only `ON UPDATE` trigger is required.
CREATE_COLLECTIONS_TS_VECTOR_TRIGGER = f'''
CREATE OR REPLACE FUNCTION update_collection_ts_vector()
    RETURNS TRIGGER AS
$$
BEGIN
    IF OLD.latest_version_id IS DISTINCT FROM NEW.latest_version_id THEN
        IF NEW.latest_version_id IS NULL THEN
            NEW.search_vector := '';
        ELSE
            NEW.search_vector := (
                SELECT {TS_VECTOR_SELECT}
                FROM main_collectionversion cv
                WHERE cv.id = NEW.latest_version_id
            );
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_ts_vector
    BEFORE UPDATE
    ON main_collection
    FOR EACH ROW
EXECUTE PROCEDURE update_collection_ts_vector();
'''

DROP_COLLECTIONS_TS_VECTOR_TRIGGER = '''
DROP TRIGGER IF EXISTS update_ts_vector ON main_collection;
DROP FUNCTION IF EXISTS update_collection_ts_vector();
'''


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0141_collection_latest_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionversion',
            name='contents',
            field=psql_fields.JSONField(default=list),
        ),
        migrations.RunSQL(
            sql=POPULATE_COLLECTIONS_TS_VECTOR,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql=CREATE_COLLECTIONS_TS_VECTOR_TRIGGER,
            reverse_sql=DROP_COLLECTIONS_TS_VECTOR_TRIGGER,
        )
    ]
