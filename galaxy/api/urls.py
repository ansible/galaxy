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

from galaxy.api import views

event_tracking_urls = [
    url(r'^influx_session/$',
        views.InfluxSession.as_view(), name='influx_session'),
    url(r'^$',
        views.InfluxMetrics.as_view(), name='influx_submit'),
]

email_urls = [
    url(r'^$', views.EmailList.as_view(), name='email_list'),
    url(r'^(?P<pk>[0-9]+)/$',
        views.EmailDetail.as_view(), name='email_detail'),
    url(r'^verification/$',
        views.EmailVerification.as_view(), name='email_verification'),
    url(r'^verification/(?P<key>[0-9a-z]+)/$',
        views.EmailVerificationDetail.as_view(), name='email_verification'),
]

user_urls = [
    url(r'^$', views.UserList.as_view(), name='user_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user_detail'),
    url(r'^(?P<pk>[0-9]+)/emails/$', views.UserEmailList.as_view(),
        name='user_email_list'),
    url(r'^(?P<pk>[0-9]+)/repos/$', views.UserRepositoriesList.as_view(),
        name='user_repositories_list'),
    url(r'^(?P<pk>[0-9]+)/subscriptions/$',
        views.UserSubscriptionList.as_view(), name='user_subscription_list'),
    url(r'^(?P<pk>[0-9]+)/starred/$', views.UserStarredList.as_view(),
        name='user_starred_list'),
    url(r'^(?P<pk>[0-9]+)/secrets/$',
        views.UserNotificationSecretList.as_view(),
        name='user_notification_secret_list'),
    url(r'^(?P<pk>[0-9]+)/token/$',
        views.UserTokenView.as_view(),
        name='user_token_view')
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
    url(r'^(?P<pk>[0-9]+)/downloads/$', views.RoleDownloads.as_view(),
        name='role_downloads'),
    url(r'^(?P<pk>[0-9]+)/versions/$', views.RoleVersionList.as_view(),
        name='role_versions'),
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
    url(r'^content/$', views.ContentSearchView.as_view(),
        name='content_search_view'),
    url(r'^roles/$', views.RoleSearchView.as_view(),
        name='roles_search_view'),
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
]

namespace_urls = [
    url(r'^$', views.NamespaceList.as_view(), name='namespace_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.NamespaceDetail.as_view(),
        name='namespace_detail'),
    url(r'^(?P<pk>[0-9]+)/provider_namespaces/$',
        views.NamespaceProviderNamespacesList.as_view(),
        name='namespace_provider_namespaces_list'),
    url(r'^(?P<pk>[0-9]+)/content/$',
        views.NamespaceContentList.as_view(),
        name='namespace_content_list'),
    url(r'^(?P<pk>[0-9]+)/owners/$',
        views.NamespaceOwnersList.as_view(),
        name='namespace_owners_list'),
]

provider_namespace_urls = [
    url(r'^$', views.ProviderNamespaceList.as_view(),
        name='provider_namespace_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.ProviderNamespaceDetail.as_view(),
        name='provider_namespace_detail'),
    url(r'^(?P<pk>[0-9]+)/repositories/$',
        views.ProviderNamespaceRepositoriesList.as_view(),
        name='provider_namespace_repositories_list'),
]

provider_urls = [
    url(r'^$', views.ProviderRootView.as_view(),
        name='provider_root_view'),
    url(r'^active/$', views.ActiveProviderList.as_view(),
        name='active_provider_list'),
    url(r'^active/(?P<pk>[0-9]+)/$', views.ActiveProviderDetail.as_view(),
        name='active_provider_detail'),
    url(r'^sources/$', views.ProviderSourceList.as_view(),
        name='provider_source_list'),
    url(r'^sources/(?P<provider_name>[A-Za-z0-9_-]+)/'
        r'(?P<provider_namespace>[A-Za-z0-9_-]+)/$',
        views.RepositorySourceList.as_view(),
        name='repository_source_list'),
    url(r'^sources/(?P<provider_name>[A-Za-z0-9_-]+)/'
        r'(?P<provider_namespace>[A-Za-z0-9_-]+)/'
        '(?P<repo_name>[A-Za-z0-9_-]+)/$',
        views.RepositorySourceDetail.as_view(),
        name='repository_source_detail'),
]

repo_urls = [
    url(r'^$', views.RepositoryList.as_view(),
        name='repository_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.RepositoryDetail.as_view(),
        name='repository_detail'),
    url(r'^(?P<pk>[0-9]+)/imports/$', views.RepositoryImportTaskList.as_view(),
        name='repository_import_task_list'),
    url(r'^(?P<pk>[0-9]+)/content/$', views.RepositoryContentList.as_view(),
        name='repository_content_list'),
    url(r'^(?P<pk>[0-9]+)/versions/$', views.RepositoryVersionList.as_view(),
        name='repository_version_list'),
    url(r'refresh/$', views.RefreshUserRepos.as_view(),
        name='refresh_user_repos'),
    url(r'stargazers/$', views.StargazerList.as_view(), name='stargazer_list'),
    url(r'stargazers/(?P<pk>[0-9]+)/$', views.StargazerDetail.as_view(),
        name='stargazer_detail'),
    url(r'subscriptions/$', views.SubscriptionList.as_view(),
        name='subscription_list'),
    url(r'subscriptions/(?P<pk>[0-9]+)/$', views.SubscriptionDetail.as_view(),
        name='subscription_detail'),
]

content_urls = [
    url(r'^$',
        views.ContentList.as_view(),
        name='content_list'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.ContentDetail.as_view(),
        name='content_detail'),

    url(r'^(?P<pk>[0-9]+)/dependencies/$',
        views.RoleDependenciesList.as_view(),
        name='content_dependencies_list'),
]

account_urls = [
    url(r'logout',
        views.LogoutView.as_view(),
        name='account_logout_view'),
]

content_block_urls = [
    url(r'^$',
        views.ContentBlockList.as_view(),
        name='content_block_list'),

    url(r'^(?P<name>[a-zA-Z0-9-_]+)/$',
        views.ContentBlockDetail.as_view(),
        name='content_block_detail'),
]

content_type_urls = [
    url(r'^$',
        views.ContentTypeList.as_view(),
        name='content_type_list'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.ContentTypeDetail.as_view(),
        name='content_type_detail'),
]

community_survey_urls = [
    url(r'^$',
        views.CommunitySurveyList.as_view(),
        name='community_survey_list'),

    url(r'^(?P<pk>[0-9]+)/$',
        views.CommunitySurveyDetail.as_view(),
        name='community_survey_detail'),
]

v1_urls = [
    url(r'^$', views.ApiV1RootView.as_view(), name='api_v1_root_view'),
    url(r'^account/', include(account_urls)),
    url(r'^me/$', views.ActiveUserView.as_view(), name='active_user_view'),
    url(r'^emails/', include(email_urls)),
    url(r'^users/', include(user_urls)),
    url(r'^roles/', include(role_urls)),
    url(r'^content/', include(content_urls)),
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
    url(r'^provider_namespaces/', include(provider_namespace_urls)),
    url(r'^repositories/', include(repo_urls)),
    url(r'^search/', include(search_urls)),
    url(r'^content_blocks/', include(content_block_urls)),
    url(r'^content_types/', include(content_type_urls)),
    url(r'^community_surveys/', include(community_survey_urls)),
]

me_urls = [
    url(
        r'^preferences/',
        views.ActiveUserPreferencesView.as_view(),
        name='active_user_preferences_view'
    ),

    url(
        r'notifications/clear/',
        views.ActiveUserClearNotificationView.as_view(),
        name='active_user_clear_notifications_view'
    ),

    url(
        r'notifications/(?P<pk>[0-9]+)/$',
        views.ActiveUserNotificationsDetailView.as_view(),
        name='active_user_notifications_view_detail'
    ),

    url(
        r'notifications/',
        views.ActiveUserNotificationsView.as_view(),
        name='active_user_notifications_view'
    ),
]

internal_urls = [
    url(r'^events/', include(event_tracking_urls)),
    url(r'^me/', include(me_urls)),
]

app_name = 'api'
urlpatterns = [
    url(r'^$', views.ApiRootView.as_view(), name='api_root_view'),
    url(r'^v1/', include(v1_urls)),
    url(r'^internal/', include(internal_urls)),
]
