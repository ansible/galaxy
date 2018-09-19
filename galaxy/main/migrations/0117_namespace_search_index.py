# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

DROP_SEARCH_VECTOR_UPDATE_TRIGGER = """
DROP TRIGGER update_search_vector ON main_content;
DROP FUNCTION on_content_update_search_vector_trigger();
"""

CREATE_SEARCH_VECTOR_UPDATE_FUNCTIONS = """
CREATE OR REPLACE FUNCTION on_content_update_search_vector_trigger()
RETURNS TRIGGER AS $$
DECLARE readme_raw TEXT;
DECLARE namespace_name TEXT;
BEGIN
  SELECT raw INTO readme_raw FROM main_readme WHERE id = NEW.readme_id;
  SELECT name INTO namespace_name
    FROM main_namespace WHERE id = NEW.namespace_id;

  NEW.search_vector :=
    setweight(to_tsvector(NEW.name), 'A')
    || setweight(to_tsvector(NEW.description), 'C')
    || setweight(to_tsvector(namespace_name), 'A')
    || setweight(to_tsvector(COALESCE(readme_raw, '')), 'D');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_search_vector
BEFORE INSERT OR UPDATE ON main_content
FOR EACH ROW EXECUTE PROCEDURE on_content_update_search_vector_trigger();
"""

# The update_search_vector vector trigger runs each time the main_content table
# is updated, so we don't actually need to recalculate the search_vector here.
# We just need to make a change to the table and let the trigger handle setting
# the vector.
SET_SEARCH_VECTOR = """
UPDATE main_content
SET search_vector = '';
"""


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0116_set_contentrule_values_20180918_1509'),
    ]

    operations = [
        migrations.RunSQL(DROP_SEARCH_VECTOR_UPDATE_TRIGGER),
        migrations.RunSQL(CREATE_SEARCH_VECTOR_UPDATE_FUNCTIONS),
        migrations.RunSQL(SET_SEARCH_VECTOR),
    ]
