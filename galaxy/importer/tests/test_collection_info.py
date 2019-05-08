import random

import pytest

from galaxy.importer.models import BaseCollectionInfo, GalaxyCollectionInfo


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
    res = BaseCollectionInfo(**base_col_info)
    assert type(res) == BaseCollectionInfo


def test_galaxy_col_info(galaxy_col_info):
    res = GalaxyCollectionInfo(**galaxy_col_info)
    assert type(res) == GalaxyCollectionInfo


def test_readme_req(galaxy_col_info):
    galaxy_col_info['readme'] = None

    # readme not required by BaseCollectionInfo
    res = BaseCollectionInfo(**galaxy_col_info)
    assert type(res) == BaseCollectionInfo

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


def test_max_tags(galaxy_col_info):
    galaxy_col_info['tags'] = [str(i) for i in range(90, 110)]
    res = GalaxyCollectionInfo(**galaxy_col_info)
    assert [str(x) for x in range(90, 110)] == res.tags

    galaxy_col_info['tags'] = [str(i) for i in range(90, 111)]
    with pytest.raises(ValueError) as exc:
        GalaxyCollectionInfo(**galaxy_col_info)
    assert 'Expecting no more than ' in str(exc)


def test_valid_semver(base_col_info):
    for ver in valid_semver:
        base_col_info['version'] = ver
        res = BaseCollectionInfo(**base_col_info)
        assert res.version == ver


def test_invalid_semver(base_col_info):
    for ver in invalid_semver:
        base_col_info['version'] = ver
        with pytest.raises(ValueError) as exc:
            BaseCollectionInfo(**base_col_info)
        assert "Expecting 'version' to be in semantic version" in str(exc)


def test_valid_license(base_col_info):
    for lic_list in valid_licenses:
        base_col_info['license'] = lic_list
        res = BaseCollectionInfo(**base_col_info)
        assert res.license == lic_list


def test_license_file(base_col_info):
    base_col_info['license'] = []
    base_col_info['license_file'] = 'my_very_own_license.txt'
    res = BaseCollectionInfo(**base_col_info)
    assert len(res.license) == 0
    assert res.license_file == 'my_very_own_license.txt'


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
        msg = ("Expecting 'license' to be a list of valid SPDX license "
               "identifiers, instead found invalid license identifiers:")
        assert msg in str(exc)
        assert str(lic) in str(exc)


def test_invalid_dep_type(base_col_info):
    base_col_info['dependencies'] = 'joe.role1: 3'
    with pytest.raises(TypeError) as exc:
        BaseCollectionInfo(**base_col_info)
    assert "'dependencies' must be <class 'dict'>" in str(exc)


def test_invalid_dep_name(base_col_info):
    base_col_info['dependencies'] = {3.3: '1.0.0'}
    with pytest.raises(ValueError) as exc:
        BaseCollectionInfo(**base_col_info)
    assert 'Expecting depencency to be string' in str(exc)


def test_invalid_dep_version(base_col_info):
    base_col_info['dependencies'] = {'joe.role1': 3}
    with pytest.raises(ValueError) as exc:
        BaseCollectionInfo(**base_col_info)
    assert 'Expecting depencency version to be string' in str(exc)


def test_non_null_str_fields(galaxy_col_info):
    galaxy_col_info['description'] = None
    res = GalaxyCollectionInfo(**galaxy_col_info)
    assert res.description is None

    galaxy_col_info['description'] = 'description of the collection'
    res = GalaxyCollectionInfo(**galaxy_col_info)
    assert res.description == 'description of the collection'

    galaxy_col_info['description'] = ['should be a string not list']
    with pytest.raises(ValueError) as exc:
        GalaxyCollectionInfo(**galaxy_col_info)
    assert "'description' must be a string" in str(exc)


def test_dependency_bad_dot_format(galaxy_col_info):
    dependent_collections = [
        'no_dot_in_collection',
        'too.many.dots',
        '.too.many.dots',
        'too.many.dots.',
    ]
    for collection in dependent_collections:
        galaxy_col_info['dependencies'] = {collection: '1.0.0'}
        with pytest.raises(ValueError) as exc:
            GalaxyCollectionInfo(**galaxy_col_info)
        assert 'Invalid dependency format' in str(exc)


def test_dependency_not_match_regex(galaxy_col_info):
    dependent_collections = [
        'empty_name.',
        '.empty_namespace',
        'a_user.{}'.format(random.choice(invalid_names)),
        '{}.gunicorn'.format(random.choice(invalid_names)),
    ]
    for collection in dependent_collections:
        galaxy_col_info['dependencies'] = {collection: '1.0.0'}
        with pytest.raises(ValueError) as exc:
            GalaxyCollectionInfo(**galaxy_col_info)
        assert 'Invalid dependency format' in str(exc)


def test_self_dependency(galaxy_col_info):
    namespace = galaxy_col_info['namespace']
    name = galaxy_col_info['name']
    galaxy_col_info['dependencies'] = {
        '{}.{}'.format(namespace, name): '1.0.0'
    }
    with pytest.raises(ValueError) as exc:
        GalaxyCollectionInfo(**galaxy_col_info)
    assert 'Cannot have self dependency' in str(exc)


def test_dep_bad_version_spec(galaxy_col_info):
    bad_version_specs = [
        {'alice.apache': 'bad_version'},
        {'alice.apache': '1.2.*'},
        {'alice.apache': ''},
        {'alice.apache': '*.*.*'},
        {'alice.apache': '>=1.0.0, <=2.0.0'},
        {'alice.apache': '>1 <2'},
    ]
    for dep in bad_version_specs:
        galaxy_col_info['dependencies'] = dep
        with pytest.raises(ValueError) as exc:
            GalaxyCollectionInfo(**galaxy_col_info)
        assert 'version spec range invalid' in str(exc)
