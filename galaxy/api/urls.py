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

from django.conf.urls import include, url
from rest_framework import routers

from galaxy.api import views


router = routers.DefaultRouter()
router.register('v1/search/roles', views.RoleSearchView,
                base_name="search-roles")

user_urls = [
    url(r'^$', views.UserList.as_view(), name='user_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user_detail'),
    url(r'^(?P<pk>[0-9]+)/repos/$', views.UserRepositoriesList.as_view(),
        name='user_repositories_list'),
    url(r'^(?P<pk>[0-9]+)/subscriptions/$',
        views.UserSubscriptionList.as_view(), name='user_subscription_list'),
    url(r'^(?P<pk>[0-9]+)/starred/$', views.UserStarredList.as_view(),
        name='user_starred_list'),
    url(r'^(?P<pk>[0-9]+)/secrets/$',
        views.UserNotificationSecretList.as_view(),
        name='user_notification_secret_list'),
]

role_urls = [
    url(r'^$', views.RoleList.as_view(), name='role_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.RoleDetail.as_view(), name='role_detail'),
    url(r'^(?P<pk>[0-9]+)/users/$', views.RoleUsersList.as_view(),
        name='role_users_list'),
    url(r'^(?P<pk>[0-9]+)/dependencies/$',
        views.RoleDependenciesList.as_view(), name='role_dependencies_list'),
    url(r'^(?P<pk>[0-9]+)/imports/$',
        views.RoleImportTaskList.as_view(), name='role_import_task_list'),
    url(r'^(?P<pk>[0-9]+)/versions/$',
        views.RoleVersionsList.as_view(), name='role_versions_list'),
    url(r'^(?P<pk>[0-9]+)/notifications/$',
        views.RoleNotificationList.as_view(), name='role_notification_list'),
    url(r'^(?P<pk>[0-9]+)/downloads/$', views.RoleDownloads.as_view(),
        name='role_downloads')
]

platform_urls = [
    url(r'^$', views.PlatformList.as_view(), name='platform_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.PlatformDetail.as_view(),
        name='platform_detail'),
]

cloud_platform_urls = [
    url(r'^$', views.CloudPlatformList.as_view(), name='cloud_platform_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.CloudPlatformDetail.as_view(),
        name='cloud_platform_detail'),
]

category_urls = [
    url(r'^$', views.CategoryList.as_view(), name='category_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.CategoryDetail.as_view(),
        name='category_detail'),
]

tag_urls = [
    url(r'^$', views.TagList.as_view(), name='tag_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.TagDetail.as_view(), name='tag_detail'),
]

search_urls = [
    url(r'^$', views.ApiV1SearchView.as_view(), name="search_view"),
    # url(r'facetedplatforms/$',           FacetedView.as_view(),
    #    kwargs={u'facet_key': u'platforms', u'model': u'Role'}, name="faceted_platforms_view"),
    # url(r'facetedtags/$',                FacetedView.as_view(),
    #    kwargs={u'facet_key': u'tags', u'model': u'Role'}, name="faceted_tags_view"),
    url(r'^platforms/$', views.PlatformsSearchView.as_view(),
        name='platforms_search_view'),
    url(r'^cloud_platforms/$', views.CloudPlatformsSearchView.as_view(),
        name='cloud_platforms_search_view'),
    url(r'^tags/$', views.TagsSearchView.as_view(), name='tags_search_view'),
    url(r'^users/$', views.UserSearchView.as_view(), name='user_search_view'),
    url(r'^top_contributors/$', views.TopContributorsList.as_view(),
        name='top_contributors_list'),
]

import_task_urls = [
    url(r'^$', views.ImportTaskList.as_view(), name='import_task_list'),
    url(r'latest/$', views.ImportTaskLatestList.as_view(),
        name='import_task_latest_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.ImportTaskDetail.as_view(),
        name='import_task_detail'),
    url(r'^(?P<pk>[0-9]+)/notifications/$',
        views.ImportTaskNotificationList.as_view(),
        name='import_task_notification_list'),
]

notification_secret_urls = [
    url(r'^$', views.NotificationSecretList.as_view(),
        name='notification_secret_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.NotificationSecretDetail.as_view(),
        name='notification_secret_detail'),
]

notification_urls = [
    url(r'^$', views.NotificationList.as_view(), name='notification_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.NotificationDetail.as_view(),
        name='notification_detail'),
    url(r'^(?P<pk>[0-9]+)/roles/$', views.NotificationRolesList.as_view(),
        name='notification_roles_list'),
    url(r'^(?P<pk>[0-9]+)/imports/$', views.NotificationImportsList.as_view(),
        name='notification_imports_list'),
]

namespace_urls = [
    url(r'^$', views.NamespaceList.as_view(), name='namespace_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.NamespaceDetail.as_view(), name='namespace_detail'),
]

provider_urls = [
    url(r'^$', views.ProviderRootView.as_view(), name='provider_root_view'),
    url(r'^active/$', views.ActiveProviderList.as_view(), name='active_provider_list'),
    url(r'^active/(?P<pk>[0-9]+)/$', views.ActiveProviderDetail.as_view(), name='active_provider_detail'),
    url(r'^sources/$', views.ProviderSourceList.as_view(), name='provider_source_list'),
]

repo_urls = [
    url(r'^$', views.ApiV1ReposView.as_view(), name="repos_view"),
    url(r'list/$', views.RepositoryList.as_view(), name='repository_list'),
    url(r'list/(?P<pk>[0-9]+)/$', views.RepositoryDetail.as_view(),
        name='repository_detail'),
    url(r'refresh/$', views.RefreshUserRepos.as_view(),
        name='refresh_user_repos'),
    url(r'stargazers/$', views.StargazerList.as_view(), name='stargazer_list'),
    url(r'stargazers/(?P<pk>[0-9]+)/$', views.StargazerDetail.as_view(),
        name='stargazer_detail'),
    url(r'subscriptions/$', views.SubscriptionList.as_view(),
        name='subscription_list'),
    url(r'subscriptions/(?P<pk>[0-9]+)/$', views.SubscriptionDetail.as_view(),
        name='subscription_detail')
]

v1_urls = [
    url(r'^$', views.ApiV1RootView.as_view(), name='api_v1_root_view'),
    url(r'^me/$', views.UserMeList.as_view(), name='user_me_list'),
    url(r'^users/', include(user_urls)),
    url(r'^roles/', include(role_urls)),
    url(r'^role_types/', views.RoleTypes.as_view(), name='role_types'),
    url(r'^categories/', include(category_urls)),
    url(r'^tags/', include(tag_urls)),
    url(r'^platforms/', include(platform_urls)),
    url(r'^cloud_platforms/', include(cloud_platform_urls)),
    url(r'^imports/', include(import_task_urls)),
    url(r'^tokens/', views.TokenView.as_view(), name='token'),
    url(r'^removerole/', views.RemoveRole.as_view(), name='remove_role'),
    url(r'^namespaces/', include(namespace_urls)),
    url(r'^notification_secrets/', include(notification_secret_urls)),
    url(r'^notifications/', include(notification_urls)),
    url(r'^providers/', include(provider_urls)),
    url(r'^repos/', include(repo_urls)),
    url(r'^search/', include(search_urls)),
]

urlpatterns = [
    url(r'^$', views.ApiRootView.as_view(), name='api_root_view'),
    url(r'^v1/', include(v1_urls)),
]

urlpatterns += router.urls
