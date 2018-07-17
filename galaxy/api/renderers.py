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

# Django REST Framework

from rest_framework import renderers


class BrowsableAPIRenderer(renderers.BrowsableAPIRenderer):
    """
    Customizations to the default browsable API renderer.
    """

    def get_rendered_html_form(self, view, method, request):
        """
        Never show auto-generated form (only raw form).
        """
        obj = getattr(view, 'object', None)
        if not self.show_form_for_method(view, method, request, obj):
            return
        if method in ('DELETE', 'OPTIONS'):
            return True  # Don't actually need to return a form
