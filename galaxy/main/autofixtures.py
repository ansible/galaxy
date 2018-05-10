# (c) 2012-2018, Ansible by Red Hat
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


import random
from django.conf import settings
from django.contrib.auth import get_user_model
from galaxy.main.models import Content, RepositoryVersion

User = get_user_model()

###################################################################################
# Autofixture Classes for generating test data

if settings.SITE_ENV == 'DEV':
    from autofixture import generators, register, AutoFixture

    class WeightedRandomBoolGenerator(generators.Generator):
        """ Generates a true X% of the time """
        def __init__(self, percent_chance=100):
            if percent_chance > 100:
                percent_chance = 100
            elif percent_chance < 0:
                percent_chance = 0
            self.percent_chance = percent_chance

        def generate(self):
            return random.randrange(100) > (100 - self.percent_chance)

    class UserNameGenerator(generators.FirstNameGenerator, generators.LastNameGenerator):
        """ Generates a username of the form f_lname """

        def __init__(self, gender=None):
            self.gender = gender
            self.all = self.male + self.female

        def generate(self):
            if self.gender == 'm':
                first_initial = random.choice(self.male)[0].lower()
            elif self.gender == 'f':
                first_initial = random.choice(self.female)[0].lower()
            else:
                first_initial = random.choice(self.all)[0].lower()
            last_name = random.choice(self.surname).lower()
            return "%s_%s" % (first_initial, last_name)

    class FullNameGenerator(generators.FirstNameGenerator, generators.LastNameGenerator):
        """ Generates a full_name of the form 'fname lname' """

        def __init__(self, gender=None):
            self.gender = gender
            self.all = self.male + self.female

        def generate(self):
            if self.gender == 'm':
                first_name = random.choice(self.male)
            elif self.gender == 'f':
                first_name = random.choice(self.female)
            else:
                first_name = random.choice(self.all)
            last_name = random.choice(self.surname)
            return "%s %s" % (first_name, last_name)

    class RoleNameGenerator(generators.Generator):
        """ Generates a role name """

        software_packages = [
            'nginx', 'httpd', 'php', 'python', 'perl', 'ruby',
            'memcache', 'mysql', 'oracle', 'couchbase', 'hadoop',
            'cobbler', 'haproxy', 'keepalived',
        ]

        def generate(self):
            return "testrole_%s" % random.choice(self.software_packages)

    class UserAutoFixture(AutoFixture):
        field_values = {
            'full_name': FullNameGenerator(),
            'username': UserNameGenerator(),
            'email': generators.EmailGenerator(),
            'password': generators.StaticGenerator('password'),
            'is_superuser': False,
            'is_staff': WeightedRandomBoolGenerator(percent_chance=3),
            'is_active': True,
        }
        follow_fk = False
        follow_m2m = False
    register(User, UserAutoFixture)

    class RoleAutoFixture(AutoFixture):
        field_values = {
            'name': RoleNameGenerator(),
            'github_user': generators.FirstNameGenerator(),
            'github_repo': generators.StringGenerator(min_length=6, max_length=10),
            'description': generators.LoremGenerator(max_length=250),
            'readme': generators.LoremHTMLGenerator(),
            'min_ansible_version': generators.StaticGenerator('1.3'),
            'issue_tracker_url': generators.URLGenerator(),
            'license': generators.StaticGenerator(''),
            'company': generators.StaticGenerator(''),
            'is_valid': generators.StaticGenerator(True),
        }
    register(Content, RoleAutoFixture)

    class RoleVersionAutoFixture(AutoFixture):
        choices = []
        for major in range(0, 3):
            for minor in range(0, 9):
                choices.append("v%d.%d" % (major, minor))
        field_values = {
            'name': generators.ChoicesGenerator(values=choices),
            'loose_version': generators.StaticGenerator("0.0"),
        }
    register(RepositoryVersion, RoleVersionAutoFixture)
