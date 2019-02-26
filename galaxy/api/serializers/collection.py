from rest_framework import serializers
from rest_framework import exceptions as drf_exc

from galaxy.pulp import schema


class UploadCollectionSerializer(serializers.Serializer):

    file = serializers.FileField(
        help_text="The collection file.",
        required=True,
    )

    sha256 = serializers.CharField(
        required=False,
        default=None,
    )

    def validate(self, data):
        super().validate(data)

        try:
            data['filename'] = schema.CollectionFilename.parse(
                data['file'].name)
        except ValueError as e:
            raise drf_exc.ValidationError(str(e))

        return data
