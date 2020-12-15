"""Serialize stt data."""

from rest_framework import serializers
from django.db.models import Max

from ..users.serializers import UserSerializer
from ..stts.serializers import STTSerializer
from .models import ReportFile
from ..users.models import User
from ..stts.models import STT


class ReportFileSerializer(serializers.ModelSerializer):
    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = ReportFile
        fields = [
            'original_filename',
            'slug',
            'extension',
            'user',
            'stt',
            'year',
            'quarter',
            'section',
        ]
    def create(self, validated_data):

        version = 1
        latest_report = ReportFile.objects.filter(
            slug__exact=validated_data['slug'],
        ).aggregate(Max('version'))

        if latest_report['version__max'] is not None:
            version = latest_report.version + 1


        return ReportFile.objects.create(
            version=version,
            **validated_data,
        )
        # I think I should have this here?

    def update():
        raise "Cannot update, reports are immutable. Create a new one instead."
        # throw error, these are immutable
