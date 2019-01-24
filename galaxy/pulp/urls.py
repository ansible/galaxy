from django.conf.urls import include, url

from . import views

pulp_urls = [
    url(r'^tasks/$',
        views.TaskViewSet.as_view({'get': 'list'})),
    url(r'^tasks/(?P<pk>[^/.]+)/$',
        views.TaskViewSet.as_view({'get': 'retrieve'}),
        name='tasks-detail'),
]

urlpatterns = [
    url(r'^v1/pulp/', include(pulp_urls)),
]
