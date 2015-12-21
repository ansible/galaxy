# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from galaxy.main.views import AuthorListView, RoleDetailView


urlpatterns = patterns('galaxy.main.views',
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
    url(r'^accounts/role/view/(?P<role>[\w\-\._:]+)$', 'accounts_role_view', name='accounts-role-view'),
    url(r'^accounts/role/refresh/(?P<id>[\w\-\._:]+)$', 'accounts_role_refresh', name='accounts-role-refresh'),
    
    # Secure Action URLs
    #url(r'^accounts/role/save$', 'accounts_role_save', name='accounts-role-save'),
    url(r'^accounts/role/delete/(?P<id>[0-9]+)$', 'accounts_role_delete', name='accounts-role-delete'),
    url(r'^accounts/role/deactivate/(?P<id>[0-9]+)$', 'accounts_role_deactivate', name='accounts-role-deactivate'),
    url(r'^accounts/role/reactivate/(?P<id>[0-9]+)$', 'accounts_role_reactivate', name='accounts-role-reactivate'),

    url(r'^([\w\-._+]+)/$', AuthorListView.as_view(), name='author-list'),
    url(r'^([\w\-._+]+)/([\w\-._+]+)/$', RoleDetailView.as_view(), name='role-detail'),
)
