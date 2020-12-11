"""Serialize stt data."""

from rest_framework import serializers

from ..users.serializers import UserSerializer
from .models import ReportFile


class ReportFileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required = True)
    stt = serializers.SerializerMethodField("get_stt")
    class Meta:
        model = ReportFile
        fields = [
            'original_name',
            'slug',
            'extension',

            'user',
            'stt',
            'year',
            'quarter',
            'section',
        ]
    def get_stt(self, obj):
        return obj.user.stt
