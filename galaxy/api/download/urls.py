from django.urls import path

from . import views


urlpatterns = [
    path('download/<filename>', views.ArtifactDownloadView.as_view(),
         name='artifact-download'),
]
