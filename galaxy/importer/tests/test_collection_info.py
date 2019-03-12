import pytest

from galaxy.importer.models import BaseCollectionInfo, GalaxyCollectionInfo


@pytest.fixture
def base_col_info():
    metadata = {
        'namespace': 'acme',
        'name': 'jenkins',
        'version': '3.5.0',
        'license': 'MIT',
        # 'min_ansible_version': '2.4',
        'authors': ['Bob Smith <b.smith@acme.com>'],
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
    'MIT',
    'Apache-2.0',
    'BSD-3-Clause',
    'CC-BY-4.0'
]

invalid_licenses = [
    'BSD',
    'Apache',
    'MIT AND Apache-2.0',
    'something_else',
    'GPL-1.0',
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


def test_invalid_license(base_col_info):
    for lic in invalid_licenses:
        base_col_info['license'] = lic
        with pytest.raises(ValueError) as exc:
            BaseCollectionInfo(**base_col_info)
        assert lic in str(exc)


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
