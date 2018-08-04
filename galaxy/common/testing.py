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

from functools import wraps

from datetime import timedelta
from django.utils import timezone

NOW = timezone.now()
LATER = NOW + timedelta(hours=1)
EARLIER = NOW - timedelta(hours=1)

TODAY = NOW
TOMORROW = TODAY + timedelta(days=1)
YESTERDAY = TODAY - timedelta(days=1)

_DATA_PROVIDER_ATTR_NAME = "galaxy_testing_data_provider"
_TEST_TEMPLATE_PREFIX = '_test_template_'


# https://stackoverflow.com/a/26853961/1243636
def merge_dicts(*dicts):
    """Merge two or more dicts"""
    new_dict = {}
    map(new_dict.update, dicts)
    return new_dict


def _make_test_function(test_template, case_idx, case):
    """Make test_smth_idx function based on template and test case data"""
    @wraps(test_template)
    def test_generated_from_template(*a, **k):
        return test_template(*a, **(merge_dicts(k, case)))

    if test_template.__doc__ is not None:
        test_generated_from_template.__doc__ = \
            test_template.__doc__.format(**case)

    test_name = '_'.join([
        'test',
        test_template.__name__[len(_TEST_TEMPLATE_PREFIX):],
        str(case_idx)
    ])
    test_generated_from_template.__name__ = test_name
    return test_generated_from_template


def resolve_templated_tests(wrapped_cls):
    for attr_name in dir(wrapped_cls):
        if not attr_name.startswith(_TEST_TEMPLATE_PREFIX):
            continue

        test_template = getattr(wrapped_cls, attr_name)

        data_providers_specs = getattr(
            test_template, _DATA_PROVIDER_ATTR_NAME, None)

        if not data_providers_specs:
            continue

        cases = [{}]

        for (name, data_provider_or_fld_name) in data_providers_specs:
            if isinstance(data_provider_or_fld_name, basestring):
                data_provider = getattr(wrapped_cls, data_provider_or_fld_name)
            else:
                data_provider = data_provider_or_fld_name

            try:
                values = data_provider()
            except TypeError:   # not callable
                values = data_provider

            assert hasattr(values, '__iter__'), values

            cases = [
                merge_dicts(existing_case, {name: value})
                for value in values
                for existing_case in cases
            ]

        delattr(wrapped_cls, attr_name)

        for i, case in enumerate(cases):
            test_function = _make_test_function(test_template, i, case)
            setattr(wrapped_cls, test_function.__name__, test_function)

    return wrapped_cls


def template_with_data_provider(data_provider_name_or_provider, name=None):
    """Attach data provider spec to templated unbound method"""

    if name is None:
        assert isinstance(data_provider_name_or_provider, basestring)
        name = data_provider_name_or_provider

    def decorator(test_template):
        assert test_template.__name__.startswith(_TEST_TEMPLATE_PREFIX)

        existing_providers = getattr(
            test_template,
            _DATA_PROVIDER_ATTR_NAME,
            []
        )

        setattr(
            test_template,
            _DATA_PROVIDER_ATTR_NAME,
            existing_providers + [(name, data_provider_name_or_provider)]
        )

        return test_template

    return decorator
