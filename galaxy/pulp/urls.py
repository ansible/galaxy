from django.conf.urls import include, url
from pulpcore.app import viewsets as pulp_viewsets

from . import views


api_urls = [
    url(r'^tasks/$',
        views.TaskViewSet.as_view({'get': 'list'})),
    url(r'^tasks/(?P<pk>[^/.]+)/$',
        views.TaskViewSet.as_view({'get': 'retrieve'}),
        name='tasks-detail'),
]

# NOTE(cutwater): Pulp views have hard dependencies on other views by
# serializing reversed URLs as references to other resources.
# Therefore we expose views that are not intended to be accessed publicly
# to standalone URL.
private_urls = [
    url(r'^workers/(?P<pk>[^/.]+)/$',
        pulp_viewsets.WorkerViewSet.as_view({'get', 'retrieve'}),
        name='workers-detail'),
    url(r'^repository/(?P<pk>[^/.]+)/',
        pulp_viewsets.RepositoryViewSet.as_view({'get', 'retrieve'}),
        name='repositories-detail'),
    url(r'^repository/(?P<repository_pk>[^/.]+)/versions/(?P<number>[^/.]+)/',
        pulp_viewsets.RepositoryVersionViewSet.as_view({'get': 'retrieve'}),
        name='versions-detail'),
    url(
        r'^repository/(?P<repository_pk>[^/.]+)/'
        r'versions/(?P<number>[^/.]+)/content/',
        pulp_viewsets.RepositoryVersionViewSet.as_view({'get': 'content'}),
        name='versions-content'),
]

urlpatterns = [
    url(r'^api/v1/', include(api_urls)),
    url(r'^_pulp/', include(private_urls)),
]
