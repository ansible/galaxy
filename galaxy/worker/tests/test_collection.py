import pytest
from django.test import TestCase

from galaxy.worker.exceptions import ImportFailed
from galaxy.importer.models import GalaxyCollectionInfo
from galaxy.worker.importers.collection import check_dependencies
from galaxy.main import models


class DependenciesTestCase(TestCase):
    @classmethod
    def setUpClass(self):
        super(DependenciesTestCase, self).setUpClass()
        ns1 = models.Namespace.objects.create(name='alice')
        col1 = models.Collection.objects.create(namespace=ns1, name='apache')
        models.CollectionVersion.objects.create(collection=col1,
                                                version='1.0.0-beta')
        ns2 = models.Namespace.objects.create(name='gunjan')
        col2 = models.Collection.objects.create(namespace=ns2, name='gunicorn')
        models.CollectionVersion.objects.create(collection=col2,
                                                version='1.2.3')
        models.CollectionVersion.objects.create(collection=col2,
                                                version='1.2.4')

    def setUp(self):
        self.metadata = {
            'namespace': 'acme',
            'name': 'jenkins',
            'version': '3.5.0',
            'license': ['MIT'],
            # 'min_ansible_version': '2.4',
            'authors': ['Bob Smith <b.smith@acme.com>'],
            'tags': ['testcases'],
            'readme': 'README.rst',
            'dependencies': {}
        }

    def test_dep_cannot_find_ns(self):
        self.metadata['dependencies'].update({'ned.nginx': '1.2.3'})
        collection_info = GalaxyCollectionInfo(**self.metadata)
        with pytest.raises(ImportFailed) as exc:
            check_dependencies(collection_info)
        assert 'namespace not in galaxy' in str(exc)

    def test_dep_cannot_find_col(self):
        self.metadata['dependencies'].update({'alice.php': '1.2.3'})
        collection_info = GalaxyCollectionInfo(**self.metadata)
        with pytest.raises(ImportFailed) as exc:
            check_dependencies(collection_info)
        assert 'collection not in galaxy' in str(exc)

    def test_dep_cannot_find_ver(self):
        missing_versions = [
            {'alice.apache': '2'},
            {'alice.apache': '1.0.1'},
            {'alice.apache': '>1.0.0'},
            {'alice.apache': '!=1.0.0'},
            {'alice.apache': '~1'},  # semantic_version error
            {'gunjan.gunicorn': '<1.2.3'},
            {'gunjan.gunicorn': '1.5'},
            {'gunjan.gunicorn': '^1.5'},
        ]
        for dep in missing_versions:
            self.metadata['dependencies'] = dep
            collection_info = GalaxyCollectionInfo(**self.metadata)
            with pytest.raises(ImportFailed) as exc:
                check_dependencies(collection_info)
            assert 'no matching version found' in str(exc)

    def test_dep_success(self):
        good_deps_ver_ranges = [
            {'alice.apache': '1.0.0'},
            {'alice.apache': '*'},
            {'alice.apache': '^1.0'},
            {'alice.apache': '>0.9.1'},
            {'gunjan.gunicorn': '1.2.3'},
            {'gunjan.gunicorn': '1.2.4'},
            {'gunjan.gunicorn': '^1.1'},
            {'gunjan.gunicorn': '!=1.2.3'},
            {'gunjan.gunicorn': '>=1.0.0,<=2.0.0'},
            {'gunjan.gunicorn': '>=1.0.0,!=1.0.5'},
        ]
        for dep in good_deps_ver_ranges:
            self.metadata['dependencies'] = dep
            res = GalaxyCollectionInfo(**self.metadata)
            assert isinstance(res, GalaxyCollectionInfo)
