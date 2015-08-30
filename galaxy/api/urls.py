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
from rest_framework import routers
from .views import RoleSearchView, FacetedView, PlatformsSearchView, TagsSearchView

router = routers.DefaultRouter()
router.register('v1/search/roles', RoleSearchView, base_name="search_roles")

def url(regex, view, kwargs=None, name=None, prefix=''):
    # Set default name from view name (if a string).
    if isinstance(view, basestring) and name is None:
        name = view
    return original_url(regex, view, kwargs, name, prefix)

user_urls = patterns('galaxy.api.views',
    url(r'^$',                         'user_list'),
    url(r'rolecontributors/$',         'user_role_contributors_list'),
    url(r'ratingcontributors/$',       'user_rating_contributors_list'),
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

platform_urls = patterns('galaxy.api.views',
    url(r'^$',                         'platform_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'platform_detail'),
)

rating_urls = patterns('galaxy.api.views',
    url(r'^$',                          'rating_list'),
    url(r'^(?P<pk>[0-9]+)/$',           'rating_detail'),
    url(r'^(?P<pk>[0-9]+)/up_votes/$',  'rating_up_votes_list'),
    url(r'^(?P<pk>[0-9]+)/down_votes/$','rating_down_votes_list'),
)


search_urls = patterns('galaxy.api.views',
    url(r'^$',                           'api_v1_search_view'),
    url(r'facetedplatforms/$',           FacetedView.as_view(), kwargs={ 'facet_key': 'platforms', 'model': 'Role' }),
    url(r'facetedtags/$',                FacetedView.as_view(), kwargs={ 'facet_key':'tags', 'model': 'Role' }),
    url(r'platforms/$',                  PlatformsSearchView.as_view(), name='platforms_search_view'),
    url(r'tags/$',                       TagsSearchView.as_view(), name='tags_search_view'),
)

v1_urls = patterns('galaxy.api.views',
    url(r'^$',                         'api_v1_root_view'),
    url(r'^me/$',                      'user_me_list'),
    url(r'^users/',                    include(user_urls)),
    url(r'^roles/',                    include(role_urls)),
    url(r'^platforms/',                include(platform_urls)),
    url(r'^ratings/',                  include(rating_urls)),
    url(r'^search/',                   include(search_urls)),
)

urlpatterns = patterns('galaxy.api.views',
    url(r'^$',                         'api_root_view'),
    url(r'^v1/',                       include(v1_urls)),
)

urlpatterns += router.urls
