# (c) 2012-2019, Ansible
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

from allauth.socialaccount import models as auth_models
from django.contrib.auth import get_user_model
from django.test import TestCase

from galaxy.main import models
from galaxy.main.signals import handlers


UserModel = get_user_model()

NAME_MIXED = 'Burnin'
NAME_UPPER = NAME_MIXED.upper()


class TestNoDuplicateNamespace(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username=NAME_MIXED, email='1@1.com')
        self.ns = models.Namespace.objects.create(name=NAME_MIXED)
        self.ns.owners.add(self.user)
        self.provider_ns = models.ProviderNamespace.objects.create(
            name=NAME_MIXED, namespace=self.ns)

    def test_no_new_database_objects_created(self):
        auth_models.SocialAccount.objects.create(
            provider='github', user=self.user, extra_data={
                'avatar_url': '',
                'login': NAME_MIXED,
            })

        handlers.user_logged_in_handler(request=None, user=self.user)

        assert models.ProviderNamespace.objects.filter(
            name__iexact=NAME_MIXED).count() == 1
        assert models.Namespace.objects.filter(
            name__iexact=NAME_MIXED).count() == 1

    def test_new_provider_namepace_created(self):
        auth_models.SocialAccount.objects.create(
            provider='github', user=self.user, extra_data={
                'avatar_url': '',
                'login': NAME_UPPER,
            })

        handlers.user_logged_in_handler(request=None, user=self.user)

        assert models.ProviderNamespace.objects.filter(
            name__iexact=NAME_MIXED).count() == 2
        assert models.Namespace.objects.filter(
            name__iexact=NAME_MIXED).count() == 1

    def test_new_lowercase_namepace_created(self):
        auth_models.SocialAccount.objects.create(
            provider='github', user=self.user, extra_data={
                'avatar_url': '',
                'login': NAME_MIXED + '2',
            })

        assert models.ProviderNamespace.objects.filter(
            name__iexact=NAME_MIXED).count() == 1
        assert models.Namespace.objects.filter(
            name__iexact=NAME_MIXED).count() == 1

        handlers.user_logged_in_handler(request=None, user=self.user)

        assert models.ProviderNamespace.objects.filter(
            name__icontains=NAME_MIXED).count() == 2
        assert self.user.namespaces.all().count() == 2
        new_ns = models.Namespace.objects.get(name__iexact=NAME_MIXED + '2')
        assert new_ns.name.islower()
