"""Serialize stt data."""

from rest_framework import serializers
from django.db.models import Max

from ..users.serializers import UserSerializer
from ..stt.serializers import STTSerializer
from .models import ReportFile


class ReportFileSerializer(serializers.ModelSerializer):
    stt = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
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

        if latest_report.exists():
            version = latest_report.version + 1


        return ReportFile.objects.create({
            **validated_data,
            version:version
        })
        # I think I should have this here?

    def update():
        raise "Cannot update, reports are immutable. Create a new one instead."
        # throw error, these are immutable
