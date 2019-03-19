from galaxy.api.internal import serializers
from galaxy.main import models
from rest_framework import generics


__all__ = [
    'CollectionList'
]


class CollectionList(generics.ListAPIView):
    model = models.Collection
    serializer_class = serializers.CollectionListSerializer
    queryset = models.Collection.objects.all()
