"""Serialize stt data."""

from django.db.models import Max

from rest_framework import serializers

from ..stts.models import STT
from ..stts.serializers import STTSerializer
from ..users.models import User
from ..users.serializers import UserSerializer
from .models import ReportFile


class ReportFileSerializer(serializers.ModelSerializer):
    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
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

        version = 1
        latest_report = ReportFile.objects.filter(
            slug__exact=validated_data["slug"],
        ).aggregate(Max("version"))

        if latest_report["version__max"] is not None:
            version = latest_report["version__max"] + 1

        return ReportFile.objects.create(
            version=version,
            **validated_data,
        )
        # I think I should have this here?

    def update():
        raise "Cannot update, reports are immutable. Create a new one instead."
