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

from django.conf.urls import include, patterns, url as original_url
from rest_framework import routers
from .views import (RoleSearchView,
                    PlatformsSearchView,
                    TagsSearchView,
                    ApiV1SearchView,
                    ApiV1ReposView,
                    UserSearchView,
                    TokenView,
                    RemoveRole,
                    RefreshUserRepos)

router = routers.DefaultRouter()
router.register('v1/search/roles', RoleSearchView, base_name="search-roles")


def url(regex, view, kwargs=None, name=None, prefix=''):
    # Set default name from view name (if a string).
    if isinstance(view, basestring) and name is None:
        name = view
    return original_url(regex, view, kwargs, name, prefix)


user_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                              'user_list'),
    url(r'^(?P<pk>[0-9]+)/$',               'user_detail'),
    url(r'^(?P<pk>[0-9]+)/repos/$',         'user_repositories_list'),
    url(r'^(?P<pk>[0-9]+)/subscriptions/$', 'user_subscription_list'),
    url(r'^(?P<pk>[0-9]+)/starred/$',       'user_starred_list'),
    url(r'^(?P<pk>[0-9]+)/secrets/$',       'user_notification_secret_list'),    
)

role_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                         'role_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'role_detail'),
    url(r'^(?P<pk>[0-9]+)/users/$',    'role_users_list'),
    url(r'^(?P<pk>[0-9]+)/dependencies/$', 'role_dependencies_list'),
    url(r'^(?P<pk>[0-9]+)/imports/$',  'role_import_task_list'),
    url(r'^(?P<pk>[0-9]+)/versions/$', 'role_versions_list'),
    url(r'^(?P<pk>[0-9]+)/notifications/$', 'role_notification_list')
)

platform_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                         'platform_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'platform_detail'),
)

category_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                         'category_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'category_detail'),
)

tag_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                         'tag_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'tag_detail'),
)

search_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                           ApiV1SearchView.as_view(), name="search_view"),
    # url(r'facetedplatforms/$',           FacetedView.as_view(),
    #    kwargs={u'facet_key': u'platforms', u'model': u'Role'}, name="faceted_platforms_view"),
    #url(r'facetedtags/$',                FacetedView.as_view(),
    #    kwargs={u'facet_key': u'tags', u'model': u'Role'}, name="faceted_tags_view"),
    url(r'platforms/$',                  PlatformsSearchView.as_view(), name='platforms_search_view'),
    url(r'tags/$',                       TagsSearchView.as_view(), name='tags_search_view'),
    url(r'users/$',                      UserSearchView.as_view(), name='user_search_view'),
    url(r'top_contributors/$',           'top_contributors_list', name='top_contributors_list'),
)

import_task_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                              'import_task_list'),
    url(r'latest/$',                        'import_task_latest_list'),
    url(r'^(?P<pk>[0-9]+)/$',               'import_task_detail'),
    url(r'^(?P<pk>[0-9]+)/notifications/$', 'import_task_notification_list'),
)

notification_secret_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                         'notification_secret_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'notification_secret_detail'),
)

notification_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                         'notification_list'),
    url(r'^(?P<pk>[0-9]+)/$',          'notification_detail'),
    url(r'^(?P<pk>[0-9]+)/roles/$',    'notification_roles_list'),
    url(r'^(?P<pk>[0-9]+)/imports/$',  'notification_imports_list'),    
)

repo_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                             ApiV1ReposView.as_view(), name="repos_view"),
    url(r'list/$',                         'repository_list'),
    url(r'list/(?P<pk>[0-9]+)/$',          'repository_detail'),
    url(r'refresh/$',                      RefreshUserRepos.as_view(), name='refresh_user_repos'),
    url(r'stargazers/$',                   'stargazer_list'),
    url(r'stargazers/(?P<pk>[0-9]+)/$',    'stargazer_detail'),
    url(r'subscriptions/$',                'subscription_list'),
    url(r'subscriptions/(?P<pk>[0-9]+)/$', 'subscription_detail'),
)

v1_urls = patterns(
    'galaxy.api.views',
    url(r'^$',                         'api_v1_root_view'),
    url(r'^me/$',                      'user_me_list'),
    url(r'^users/',                    include(user_urls)),
    url(r'^roles/',                    include(role_urls)),
    url(r'^role_types/',               'role_types'),
    url(r'^categories/',               include(category_urls)),
    url(r'^tags/',                     include(tag_urls)),
    url(r'^platforms/',                include(platform_urls)),
    url(r'^imports/',                  include(import_task_urls)),
    url(r'^tokens/',                   TokenView.as_view(), name='token'),
    url(r'^removerole/',               RemoveRole.as_view(), name='remove_role'),
    url(r'^notification_secrets/',     include(notification_secret_urls)),
    url(r'^notifications/',            include(notification_urls)),
    url(r'^repos/',                    include(repo_urls)),
    url(r'^search/',                   include(search_urls)),
)

urlpatterns = patterns(
    'galaxy.api.views',
    url(r'^$',                         'api_root_view'),
    url(r'^v1/',                       include(v1_urls)),
)

urlpatterns += router.urls
