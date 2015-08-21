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

# Copyright (c) 2013 AnsibleWorks, Inc.
# All Rights Reserved.

from django.conf.urls import include, patterns, url as original_url

def url(regex, view, kwargs=None, name=None, prefix=''):
    # Set default name from view name (if a string).
    if isinstance(view, basestring) and name is None:
        name = view
    return original_url(regex, view, kwargs, name, prefix)

user_urls = patterns('galaxy.api.views',
    url(r'^$',                         'user_list'),
    url(r'top/$',                      'user_top_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'user_detail'),
    url(r'^(?P<pk>[0-9]+)/roles/$',    'user_roles_list'),
    url(r'^(?P<pk>[0-9]+)/ratings/$',  'user_ratings_list'),
)

role_urls = patterns('galaxy.api.views',
    url(r'^$',                         'role_list'),
    url(r'top/$',                      'role_top_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'role_detail'),
    url(r'^(?P<pk>[0-9]+)/users/$',    'role_users_list'),
    url(r'^(?P<pk>[0-9]+)/authors/$',  'role_authors_list'),
    url(r'^(?P<pk>[0-9]+)/dependencies/$', 'role_dependencies_list'),
    url(r'^(?P<pk>[0-9]+)/imports/$',  'role_imports_list'),
    url(r'^(?P<pk>[0-9]+)/ratings/$',  'role_ratings_list'),
    url(r'^(?P<pk>[0-9]+)/versions/$', 'role_versions_list'),
)

category_urls = patterns('galaxy.api.views',
    url(r'^$',                         'category_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'category_detail'),
)

platform_urls = patterns('galaxy.api.views',
    url(r'^$',                         'platform_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'platform_detail'),
)

rating_urls = patterns('galaxy.api.views',
    url(r'^$',                         'rating_list'),
    url(r'^(?P<pk>[0-9]+)/$',           'rating_detail'),
    url(r'^(?P<pk>[0-9]+)/up_votes/$',  'rating_up_votes_list'),
    url(r'^(?P<pk>[0-9]+)/down_votes/$','rating_down_votes_list'),
)

v1_urls = patterns('galaxy.api.views',
    url(r'^$',                         'api_v1_root_view'),
    url(r'^me/$',                      'user_me_list'),
    url(r'^users/',                    include(user_urls)),
    url(r'^roles/',                    include(role_urls)),
    url(r'^categories/',               include(category_urls)),
    url(r'^platforms/',                include(platform_urls)),
    url(r'^ratings/',                  include(rating_urls)),
)

urlpatterns = patterns('galaxy.api.views',
    url(r'^$',                         'api_root_view'),
    url(r'^v1/',                       include(v1_urls)),
)
