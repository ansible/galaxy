import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from galaxy.importer.models import BaseCollectionInfo, GalaxyCollectionInfo
from galaxy.main import models



class CollectionViewTests(TestCase):

    def setUp(self):
        self.namespace = models.Namespace.objects.create(
            name='mynamespace',
        )
        self.collection = models.Collection.objects.create(
            namespace=self.namespace,
            name='mycollection',
        )
        self.version = models.CollectionVersion.objects.create(
            collection=self.collection,
            version='1.0.0',
            contents='{}',
        )

    def test_get_collections(self):
        client = APIClient()
        resp = client.get("/api/internal/ui/collections/")
        results = resp.json()['results']

        collection = results[0]

        assert collection['namespace'] == self.namespace.id
        assert collection['name'] == self.collection.name
        assert collection['latest_version']['version'] == self.version.version
