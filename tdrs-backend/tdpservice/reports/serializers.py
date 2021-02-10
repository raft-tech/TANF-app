"""Serialize stt data."""

from rest_framework import serializers
from ..stts.models import STT
from ..users.models import User
from .models import ReportFile


class PresignedUrlInputSerializer(serializers.Serializer):
    """Serializer for input to create a presigned url for s3."""

    file_name = serializers.CharField(max_length=200)
    file_type = serializers.CharField(max_length=50)


class ReportFileSerializer(serializers.ModelSerializer):
    """Serializer for Report files."""

    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        """Metadata."""

        model = ReportFile
        fields = [
            "original_filename",
            "slug",
            "extension",
            "user",
            "stt",
            "year",
            "quarter",
            "section",
        ]

    def create(self, validated_data):
        """Create a new entry with a new version number."""
        return ReportFile.create_new_version(validated_data)

    def update():
        """Throw an error if a user tries to update a report."""
        raise "Cannot update, reports are immutable. Create a new one instead."
