# galaxy-elasticsearch:2.4.6

## Why

Galaxy requires Elasticsearch version 2 due to the following:

- The `drf-haystack` module does not support Elasticsearch 5. See https://github.com/django-haystack/django-haystack/issues/1383
- If the above gets resolved, we're pinned to `drf-haystack 1.5.6` until we upgrade to a newer release of Django

Keep in mind that moving to Elasticsearch 6 will depend on both `drf-haystack` and `elasticsearch-dsl`. At the time of this writing, `elasticsearch-dsl` only supported Elasticsearch 5.

This Dockerfile build context attempts to build an Elasticsearch 2 image capable of running on OpenShift 3.

## How

The image is available on Docker Hub as `ansible/galaxy-elasticsearch:2.4.6`. If you want to build it locally, run the following: `docker build . -t galaxy-elasticsearch:2.4.6`.

## Future

Galaxy will likely move away from Elasticsearch in order to eliminate the extra dependencies and complexities. We're evaluating Postgres full text search. For more, keep an eye on [#193](https://github.com/ansible/galaxy/issues/193).
