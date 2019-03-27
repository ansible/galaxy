import pytest
from django.test import TestCase

from galaxy.importer.models import BaseCollectionInfo, GalaxyCollectionInfo
from galaxy.main import models


@pytest.fixture
def base_col_info():
    metadata = {
        'namespace': 'acme',
        'name': 'jenkins',
        'version': '3.5.0',
        'license': ['MIT'],
        # 'min_ansible_version': '2.4',
        'tags': ['testcases']
    }
    return metadata


@pytest.fixture
def galaxy_col_info(base_col_info):
    base_col_info['readme'] = 'README.rst'
    base_col_info['authors'] = ['Bob Smith <b.smith@acme.com>']
    return base_col_info


valid_names = [
    'my_namespace',
    'my_name',
    'roles75',
    'nginx',
    'nginx_',
    'deploy4py_script',
]

invalid_names = [
    '_leading_underscore',
    'has-some-dashes',
    '5tarts_with_number',
    '030',
    '0x4e3',
    'has space',
    'hasUpperCase',
    'double__under',
    'invalid#char',
    'inv@lid/char',
    'no.dots',
]

valid_tags = [
    'deployment',
    'fedora',
    'fedora29'
    '4ubuntu',
    'alloneword',
    '007',
    '0x4e3'
]

invalid_tags = [
    'bad_tag',
    'bad-tag',
    'bad tag',
    'bad.tag',
    '_deploy',
    'inv@lid/char',
]

valid_semver = [
    '1.2.3',
    '1.0.0-beta',
    '2.0.0-rc.2',
    '4.6.21'
]

invalid_semver = [
    '2',
    '1.2.3a',
    '2.0.02',
    '1.2.beta',
    '3,4',
    '3.4.0.4',
    'latest',
    'v0',
]

valid_licenses = [
    ['MIT'],
    ['Apache-2.0'],
    ['BSD-3-Clause'],
    ['CC-BY-4.0', 'MIT']
]

invalid_licenses = [
    ['BSD'],
    ['Apache'],
    ['MIT AND Apache-2.0'],
    ['something_else'],
    ['CC-BY-4.0', 'MIT', 'bad_license_id']
]


def test_base_col_info(base_col_info):
    BaseCollectionInfo(**base_col_info)


def test_galaxy_col_info(galaxy_col_info):
    GalaxyCollectionInfo(**galaxy_col_info)


def test_readme_req(galaxy_col_info):
    galaxy_col_info['readme'] = None
    # readme not required by BaseCollectionInfo
    BaseCollectionInfo(**galaxy_col_info)
    # readme required by GalaxyCollectionInfo
    with pytest.raises(ValueError) as exc:
        GalaxyCollectionInfo(**galaxy_col_info)
    assert "'readme' is required by galaxy" in str(exc)


def test_valid_names(base_col_info):
    for name in valid_names:
        base_col_info['name'] = name
        res = BaseCollectionInfo(**base_col_info)
        assert res.name == name


def test_invalid_names(base_col_info):
    for name in invalid_names:
        base_col_info['name'] = name
        with pytest.raises(ValueError) as exc:
            BaseCollectionInfo(**base_col_info)
        assert name in str(exc)


def test_valid_tags(base_col_info):
    for tag in valid_tags:
        base_col_info['tags'] += [tag]
    res = BaseCollectionInfo(**base_col_info)
    assert tag in res.tags


def test_invalid_tags(base_col_info):
    for tag in invalid_tags:
        base_col_info['tags'] = [tag]
        with pytest.raises(ValueError) as exc:
            BaseCollectionInfo(**base_col_info)
        assert tag in str(exc)


def test_valid_semver(base_col_info):
    for ver in valid_semver:
        base_col_info['version'] = ver
        BaseCollectionInfo(**base_col_info)


def test_invalid_semver(base_col_info):
    for ver in invalid_semver:
        base_col_info['version'] = ver
        with pytest.raises(ValueError) as exc:
            BaseCollectionInfo(**base_col_info)
        assert 'version' in str(exc)


def test_valid_license(base_col_info):
    for lic in valid_licenses:
        base_col_info['license'] = lic
        BaseCollectionInfo(**base_col_info)


def test_license_file(base_col_info):
    base_col_info['license'] = []
    base_col_info['license_file'] = 'my_very_own_license.txt'
    BaseCollectionInfo(**base_col_info)


def test_empty_lic_and_lic_file(base_col_info):
    base_col_info['license'] = []
    with pytest.raises(ValueError) as exc:
        BaseCollectionInfo(**base_col_info)
    assert "values for 'license' or 'license_file' are required" in str(exc)


def test_license_not_list_of_str(base_col_info):
    base_col_info['license'] = 'MIT'
    with pytest.raises(ValueError) as exc:
        BaseCollectionInfo(**base_col_info)
    assert "Expecting 'license' to be a list of strings" in str(exc)


def test_invalid_license(base_col_info):
    for lic in invalid_licenses:
        base_col_info['license'] = lic
        with pytest.raises(ValueError) as exc:
            BaseCollectionInfo(**base_col_info)
        assert "Expecting 'license' to be a list of valid" in str(exc)


def test_invalid_dep_dict(base_col_info):
    base_col_info['dependencies'] = {'joe.role1': 3}
    with pytest.raises(ValueError) as exc:
        BaseCollectionInfo(**base_col_info)
    assert 'string' in str(exc)


def test_non_null_str_fields(galaxy_col_info):
    galaxy_col_info['description'] = None
    GalaxyCollectionInfo(**galaxy_col_info)

    galaxy_col_info['description'] = 'description of the collection'
    GalaxyCollectionInfo(**galaxy_col_info)

    galaxy_col_info['description'] = ['should be a string not list']
    with pytest.raises(ValueError) as exc:
        GalaxyCollectionInfo(**galaxy_col_info)
    assert 'description' in str(exc)


class DependenciesTestCase(TestCase):
    @classmethod
    def setUpClass(self):
        super(DependenciesTestCase, self).setUpClass()
        # create namespace and coll objs into the database
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
        with pytest.raises(ValueError) as exc:
            GalaxyCollectionInfo(**self.metadata)
        assert 'namespace not in galaxy' in str(exc)

    def test_dep_cannot_find_col(self):
        self.metadata['dependencies'].update({'alice.php': '1.2.3'})
        with pytest.raises(ValueError) as exc:
            GalaxyCollectionInfo(**self.metadata)
        assert 'collection not in galaxy' in str(exc)

    def test_dep_bad_version_spec(self):
        bad_version_specs = [
            {'alice.apache': 'bad_version'},
            {'alice.apache': '1.2.*'},
            {'alice.apache': '>=1.0.0, <=2.0.0'},
        ]
        for dep in bad_version_specs:
            self.metadata['dependencies'] = dep
            with pytest.raises(ValueError) as exc:
                GalaxyCollectionInfo(**self.metadata)
            assert 'version spec range invalid' in str(exc)

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
            with pytest.raises(ValueError) as exc:
                GalaxyCollectionInfo(**self.metadata)
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
