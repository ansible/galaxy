# (c) 2012-2017, Ansible by Red Hat
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

from django import test

from galaxy.main import views


class TestErrorHandlers(test.SimpleTestCase):

    def setUp(self):
        self.factory = test.RequestFactory()

    def test_handle_400_view(self):
        request = self.factory.get('/path')
        response = views.handle_400_view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("The requested page could not be found.",
                      response.content)

    def test_handle_404_view(self):
        request = self.factory.get('/path')
        response = views.handle_404_view(request)
        self.assertEqual(response.status_code, 404)
        self.assertIn("The requested page could not be found.",
                      response.content)

    def test_handle_500_view(self):
        request = self.factory.get('/path')
        response = views.handle_500_view(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn("An error occurred while loading the requested page.",
                      response.content)
