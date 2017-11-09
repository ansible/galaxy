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

from django.conf.urls import patterns, url
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.contrib.staticfiles.views import serve as serve_staticfiles
from django.views.static import serve as serve_static

from galaxy.main.views import RoleListView, RoleDetailView, NamespaceListView

urlpatterns = patterns(
    'galaxy.main.views',
    # Non-secure URLs
    url(r'^$', 'home', name='home'),
    url(r'^explore$', 'explore', name='explore'),
    url(r'^intro$', 'intro', name='intro'),
    url(r'^accounts/landing[/]?$', 'accounts_landing', name='accounts-landing'),
    url(r'^list$', 'list_category', name='list-category'),
    url(r'^detail$', 'detail_category', name='detail-category'),
    url(r'^roleadd$', 'role_add_view', name='role-add-category'),
    url(r'^imports$', 'import_status_view', name='import-status'),

    # Logged in/secured URLs
    url(r'^accounts/connect/$', 'accounts_connect'),
    url(r'^accounts/connect/success/$', 'accounts_connect_success', name='accounts-connect-success'),
    url(r'^accounts/profile/$', 'accounts_profile', name='accounts-profile'),

    url(r'^authors/$', NamespaceListView.as_view(), name='namespace-list'),
    url(r'^([\w\-._+]+)/$', RoleListView.as_view(), name='role-list'),
    url(r'^([\w\-._+]+)/([\w\-._+]+)/$', RoleDetailView.as_view(), name='role-detail'),
)

# FIX
if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$',
            never_cache(serve_staticfiles))
    ]
else:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve_static,
            kwargs={'document_root': settings.STATIC_ROOT})
    ]
