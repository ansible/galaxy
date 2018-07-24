# -*- coding: utf-8 -*-
# (c) 2012-2018, Ansible
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

from operator import attrgetter

from django.core.exceptions import ValidationError
from django.db.models.manager import Manager
from django.db.utils import DataError, IntegrityError

import mock
import pytest

from galaxy.accounts.models import CustomUser
from galaxy.main.models import Namespace
from galaxy.common.testing import NOW, LATER


@pytest.fixture(scope="module", autouse=True)
def clean_db(django_db_blocker):
    with django_db_blocker.unblock():
        Namespace.objects.all().delete()


def get_valid_defaults():
    return [
        {
            "name": "NAMESPACE_1",
            "description": "DESCRIPTION_1",
            "avatar_url": "avatar_url_1",
            "location": "LOCATION_1",
            "company": "COMPANY_1",
            "email": "mail-1@example.com",
            "html_url": "html_url_1",
        },
        {
            "name": "NAMESPACE_2",
            "description": "DESCRIPTION_2",
            "avatar_url": "avatar_url_2",
            "location": "LOCATION_2",
            "company": "COMPANY_2",
            "email": "mail-2@example.com",
            "html_url": "html_url_2",
        }
    ]


def test_manager_class():
    assert isinstance(Namespace.objects, Manager)


@pytest.mark.model_fields_validation
@pytest.mark.django_db()
@mock.patch('django.utils.timezone.now', side_effect=[NOW, NOW, LATER])
def test_create_minimal(fake_now):
    # no mandatory fields
    namespace = Namespace.objects.create()
    assert isinstance(namespace, Namespace)

    # check defaults
    assert namespace.name == ""
    assert namespace.description == ""
    assert list(namespace.owners.all()) == []
    assert namespace.avatar_url is None
    assert namespace.location is None
    assert namespace.company is None
    assert namespace.email is None
    assert namespace.html_url is None
    assert namespace.created == NOW
    assert namespace.modified == NOW

    namespace.save()
    assert namespace.created == NOW
    assert namespace.modified != NOW
    assert namespace.modified == LATER
    assert fake_now.call_count == 3


@pytest.mark.model_fields_validation
@pytest.mark.django_db()
def test_defaults_ok():
    # does not raise
    Namespace.objects.create(**get_valid_defaults()[0]).full_clean()


# --- tests for blank fields ---


@pytest.mark.parametrize("field_name", [
    "name",
])
@pytest.mark.model_fields_validation
@pytest.mark.django_db()
def test_field_can_not_be_blank(field_name):
    create_kwargs = get_valid_defaults()[0]
    create_kwargs[field_name] = ""

    with pytest.raises(ValidationError, message=field_name) as excinfo:
        Namespace(**create_kwargs).full_clean()

    assert str(excinfo.value) == str({
        field_name: [
            u'This field cannot be blank.'
        ]
    })


@pytest.mark.parametrize("field_name", [
    "avatar_url",
    "location",
    "company",
    "email",
    "html_url",
])
@pytest.mark.model_fields_validation
@pytest.mark.django_db()
def test_field_can_be_blank(field_name):
    create_kwargs = get_valid_defaults()[0]
    create_kwargs[field_name] = ""
    try:
        Namespace(**create_kwargs).full_clean()
    except ValidationError:
        pytest.fail('"{field_name}" should be allowed to be blank')


# --- tests for nullable fields ---


@pytest.mark.parametrize("field_name", [
    "name",
])
@pytest.mark.model_fields_validation
@pytest.mark.django_db()
def test_field_can_not_be_null(field_name):
    create_kwargs = get_valid_defaults()[0]
    create_kwargs[field_name] = None

    with pytest.raises(ValidationError, message=field_name) as excinfo:
        Namespace(**create_kwargs).full_clean()

    assert str(excinfo.value) == str({
        field_name: [
            u'This field cannot be null.'
        ]
    })


@pytest.mark.parametrize("field_name", [
    "avatar_url",
    "location",
    "company",
    "email",
    "html_url",
])
@pytest.mark.model_fields_validation
@pytest.mark.django_db()
def test_field_can_be_null(field_name):
    create_kwargs = get_valid_defaults()[0]
    create_kwargs[field_name] = None
    try:
        Namespace(**create_kwargs).full_clean()
    except ValidationError:
        pytest.fail('"{field_name}" should be allowed to be null')


# --- tests for limited fields ---


@pytest.mark.parametrize("field_name,field_len", [
    ("name", 512),
    ("avatar_url", 256),
    ("location", 256),
    ("company", 256),
    ("email", 256),
    ("html_url", 256)
])
@pytest.mark.model_fields_validation
@pytest.mark.django_db()
def test_field_is_limited_in_db(field_name, field_len):
    create_kwargs = get_valid_defaults()[0]
    create_kwargs[field_name] = 'a' * field_len
    # does not raise
    Namespace.objects.create(**create_kwargs)

    create_kwargs = get_valid_defaults()[0]
    create_kwargs[field_name] = 'a' * (field_len + 1)

    with pytest.raises(DataError, message=field_name) as excinfo:
        Namespace.objects.create(**create_kwargs)

    assert str(excinfo.value) == (
        'value too long for type character varying({field_len})\n'
    ).format(
        field_len=field_len
    )


@pytest.mark.parametrize("field_name,field_len", [
    ("name", 512),
    ("avatar_url", 256),
    ("location", 256),
    ("company", 256),
    ("email", 256),
    ("html_url", 256)
])
@pytest.mark.model_fields_validation
@pytest.mark.django_db()
def test_field_is_limited(field_name, field_len):
    create_kwargs = get_valid_defaults()[0]
    create_kwargs[field_name] = 'a' * field_len
    # does not raise
    Namespace(**create_kwargs).full_clean()

    create_kwargs = get_valid_defaults()[0]
    create_kwargs[field_name] = 'a' * (field_len + 1)

    with pytest.raises(ValidationError, message=field_name) as excinfo:
        Namespace(**create_kwargs).full_clean()

    assert str(excinfo.value) == str({
        field_name: [
            (
                u'Ensure this value has at most {field_len} characters '
                '(it has {given_length}).'
            ).format(
                field_len=field_len,
                given_length=field_len + 1
            )
        ]
    })


# --- tests for indexed/unique fields ---


@pytest.mark.parametrize("field_name", [
    "name",
])
@pytest.mark.model_fields_validation
@pytest.mark.django_db()
def test_field_is_unique(field_name):
    create_kwargs_0 = get_valid_defaults()[0]
    create_kwargs_1 = get_valid_defaults()[1]
    create_kwargs_1[field_name] = create_kwargs_0[field_name]

    Namespace.objects.create(**create_kwargs_0)

    with pytest.raises(IntegrityError, message=field_name) as excinfo:
        Namespace.objects.create(**create_kwargs_1)

    assert str(excinfo.value) == (
        'duplicate key value violates unique constraint '
        '"main_namespace_{field_name}_key"\n'
        'DETAIL:  Key ({field_name})=({field_value}) already exists.\n'
    ).format(
        field_name=field_name,
        field_value=create_kwargs_1[field_name]
    )


@pytest.mark.parametrize("field_name", [
    "avatar_url",
    "location",
    "company",
    "email",
    "html_url",
])
@pytest.mark.model_fields_validation
@pytest.mark.django_db()
def test_field_is_not_unique(field_name):
    create_kwargs_0 = get_valid_defaults()[0]
    create_kwargs_1 = get_valid_defaults()[1]
    create_kwargs_1[field_name] = create_kwargs_0[field_name]

    Namespace.objects.create(**create_kwargs_0)

    try:
        Namespace.objects.create(**create_kwargs_1)
    except IntegrityError:
        pytest.fail('"{field_name}" should be not unique')


# --- tests for custom methods ---


@pytest.mark.model_methods
@pytest.mark.django_db()
def test_convert_to_string():
    # __str__ will return name
    create_kwargs = get_valid_defaults()[0]
    namespace = Namespace.objects.create(**create_kwargs)

    assert str(namespace) == (
        create_kwargs["name"] + "-" + str(namespace.id)
    )


@pytest.mark.model_methods
@pytest.mark.django_db()
def test_repr():
    # __str__ returns name, but it did not affected __repr__
    create_kwargs = get_valid_defaults()[0]
    namespace = Namespace.objects.create(**create_kwargs)

    assert repr(namespace) == (
        '<Namespace: {name}-{namespace_id}>'
    ).format(
        name=namespace.name,
        namespace_id=namespace.id
    )


@pytest.mark.model_methods
@pytest.mark.django_db()
def test_get_absolute_url():
    # this method creates url with namespace id
    create_kwargs = get_valid_defaults()[0]
    namespace = Namespace.objects.create(**create_kwargs)

    assert namespace.get_absolute_url() == (
        "/api/v1/namespaces/{namespace_id}/"
    ).format(namespace_id=namespace.id)


# TODO:
@pytest.mark.skip
def test_content_counts():
    pass


# --- tests for relations --


@pytest.mark.django_db()
def test_may_have_many_owners():
    create_kwargs = get_valid_defaults()[0]
    namespace = Namespace.objects.create(**create_kwargs)
    default_user_1 = CustomUser.objects.create(
        username="USER_1",
        email="user-1@example.com"
    )
    default_user_2 = CustomUser.objects.create(
        username="USER_2",
        email="user-2@example.com"
    )

    namespace.owners.add(default_user_1, default_user_2)
    namespace.save()

    namespace = Namespace.objects.get(id=namespace.id)

    get_id = attrgetter("id")
    assert (
        map(get_id, namespace.owners.all()) ==
        map(get_id, [default_user_1, default_user_2])
    )


@pytest.mark.django_db()
def test_many_namespaces_may_have_same_owner():
    create_kwargs_0 = get_valid_defaults()[0]
    create_kwargs_1 = get_valid_defaults()[1]
    namespace_0 = Namespace.objects.create(**create_kwargs_0)
    namespace_1 = Namespace.objects.create(**create_kwargs_1)

    default_user_1 = CustomUser.objects.create(
        username="USER_1",
        email="user-1@example.com"
    )

    # add owners
    namespace_0.owners.add(default_user_1)
    namespace_0.save()

    namespace_1.owners.add(default_user_1)
    namespace_1.save()

    # reload models
    namespace_0 = Namespace.objects.get(id=namespace_0.id)
    namespace_1 = Namespace.objects.get(id=namespace_1.id)

    get_id = attrgetter("id")
    assert (
        map(get_id, namespace_0.owners.all()) ==
        map(get_id, namespace_1.owners.all()) ==
        [default_user_1.id]
    )
