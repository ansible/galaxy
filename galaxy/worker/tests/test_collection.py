import pytest
from django.test import TestCase

from galaxy.worker.exceptions import ImportFailed
from galaxy.importer.models import GalaxyCollectionInfo
from galaxy.worker.importers.collection import check_dependencies
from galaxy.main import models


class TestDependencies(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
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
        col3 = models.Collection.objects.create(namespace=ns2, name='gnu_app')
        models.CollectionVersion.objects.create(collection=col3,
                                                version='3.0.0')

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
        at_least_one_missing = [
            {
                'ned.nginx': '1.2.3',
            },
            {
                'dne.nginx': '9.9.9',
                'ned.nginx': '1.2.3',
                'alice.apache': '*',
            },
            {
                'alice.apache': '*',
                'gunjan.gnu_app': '3.0.0',
                'dne.nginx': '9.9.9',
            },
        ]
        for dep in at_least_one_missing:
            self.metadata['dependencies'] = dep
            collection_info = GalaxyCollectionInfo(**self.metadata)
            with pytest.raises(ImportFailed) as exc:
                check_dependencies(collection_info)
            assert 'namespace not in galaxy' in str(exc)

    def test_dep_cannot_find_col(self):
        at_least_one_missing = [
            {
                'alice.php': '1.2.3',
            },
            {
                'alice.apache': '*',
                'alice.php': '1.2.3',
            },
            {
                'alice.apache': '*',
                'gunjan.gnu_app': '3.0.0',
                'gunjan.doesnotexist': '9.9.9',
            },
        ]
        for dep in at_least_one_missing:
            self.metadata['dependencies'] = dep
            collection_info = GalaxyCollectionInfo(**self.metadata)
            with pytest.raises(ImportFailed) as exc:
                check_dependencies(collection_info)
            assert 'collection not in galaxy' in str(exc)

    def test_fail_on_unfound_version(self):
        at_least_one_missing = [
            {'alice.apache': '1.0.1'},
            {'alice.apache': '!=1.0.0'},
            {'gunjan.gunicorn': '^1.5'},
            {'alice.apache': '~1'},  # semantic_version error
            {
                'alice.apache': '2',
                'gunjan.gunicorn': '<1.2.3',
            },
            {
                'gunjan.gunicorn': '<1.2.3',
                'alice.apache': '2',
            },
            {
                'alice.apache': '1.0.0',  # findable
                'gunjan.gunicorn': '1.5',
            },
            {
                'gunjan.gunicorn': '1.5',
                'alice.apache': '1.0.0',  # findable
            },
            {
                'gunjan.gunicorn': '1.2.4',  # findable
                'gunjan.gnu_app': '3.0.0',  # findable
                'alice.apache': '>1.0.0',
            },
            {
                'gunjan.gunicorn': '1.2.4',  # findable
                'alice.apache': '>1.0.0',
                'gunjan.gnu_app': '3.0.0',  # findable
            },
        ]
        for dep in at_least_one_missing:
            self.metadata['dependencies'] = dep
            collection_info = GalaxyCollectionInfo(**self.metadata)
            with pytest.raises(ImportFailed) as exc:
                check_dependencies(collection_info)
            assert 'no matching version found' in str(exc)

    def test_pass_find_all_versions(self):
        findable_versions = [
            {
                'alice.apache': '*',
                'gunjan.gunicorn': '!=1.2.3',
                'gunjan.gnu_app': '3.0.0',
            },
            {
                'alice.apache': '^1.0',
                'gunjan.gunicorn': '^1.1',
            },
            {
                'alice.apache': '>0.9.1',
                'gunjan.gunicorn': '1.2.3',
            },
            {
                'gunjan.gunicorn': '1.2.3',
                'alice.apache': '>0.9.1',
            },
            {},
            {'alice.apache': '1.0.0'},
            {'gunjan.gunicorn': '1.2.4'},
            {'gunjan.gunicorn': '>=1.0.0,<=2.0.0'},
            {'gunjan.gunicorn': '>=1.0.0,!=1.0.5'},
        ]
        for dep in findable_versions:
            self.metadata['dependencies'] = dep
            collection_info = GalaxyCollectionInfo(**self.metadata)
            check_dependencies(collection_info)
            assert isinstance(collection_info, GalaxyCollectionInfo)
