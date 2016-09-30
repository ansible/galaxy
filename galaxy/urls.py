# (c) 2012-2016, Ansible by Red Hat
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

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
import autofixture

handler404 = 'galaxy.main.views.handle_404_view'
handler400 = 'galaxy.main.views.handle_400_view'
handler500 = 'galaxy.main.views.handle_500_view'

admin.autodiscover()
autofixture.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^accounts/', include('allauth.urls')),
    url(r'^api/', include('galaxy.api.urls', namespace='api', app_name='api')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^avatar/', include('avatar.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots\.txt$', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
    url(r'', include('galaxy.main.urls', namespace='main', app_name='main')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls))
    )
