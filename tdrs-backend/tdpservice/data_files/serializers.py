"""Serialize stt data."""
import logging
from rest_framework import serializers
from tdpservice.parsers.models import ParserError
from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.models import DataFile, ReparseFileMeta
from tdpservice.data_files.validators import (
    validate_file_extension,
    validate_file_infection,
)
from tdpservice.security.models import ClamAVFileScan
from tdpservice.stts.models import STT
from tdpservice.users.models import User
from tdpservice.parsers.serializers import DataFileSummarySerializer
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
logger = logging.getLogger(__name__)



# class ReparseMetaSerializer(serializers.ModelSerializer):
#     """Serializer for ReparseMeta class."""

#     class Meta:
#         """Meta class."""

#         model = ReparseMeta
#         fields = ['created_at']

class ReparseFileMetaSerializer(serializers.ModelSerializer):
    """Serializer for ReparseFileMeta class."""

    # reparse_meta = ReparseMetaSerializer(many=False, read_only=True)

    class Meta:
        """Meta class."""

        model = ReparseFileMeta
        fields = [
            'finished',
            'success',
            'started_at',
            'finished_at',
            # 'reparse_meta',
        ]

class DataFileSerializer(serializers.ModelSerializer):
    """Serializer for Data files."""

    file = serializers.FileField(write_only=True)
    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    ssp = serializers.BooleanField(write_only=True)
    has_error = serializers.SerializerMethodField()
    summary = DataFileSummarySerializer(many=False, read_only=True)
    # reparse_file_metas = ReparseFileMetaSerializer(many=True, read_only=True)
    reparse_file_metas = serializers.SerializerMethodField()

    class Meta:
        """Metadata."""

        model = DataFile
        fields = [
            "file",
            "id",
            "original_filename",
            "slug",
            "extension",
            "user",
            "stt",
            "year",
            "quarter",
            "section",
            "created_at",
            "ssp",
            "submitted_by",
            'version',
            's3_location',
            's3_versioning_id',
            'has_error',
            'summary',
            'reparse_file_metas',
        ]

        read_only_fields = ("version",)

    def get_has_error(self, obj):
        """Return whether the file has an error."""
        parser_errors = ParserError.objects.filter(file=obj.id)
        return len(parser_errors) > 0

    def get_reparse_file_metas(self, instance):
        reparse_file_metas = instance.reparse_file_metas.all().order_by('-finished_at')  # .first() ?
        return ReparseFileMetaSerializer(reparse_file_metas, many=True, read_only=True).data  # many=False

    def create(self, validated_data):
        """Create a new entry with a new version number."""
        ssp = validated_data.pop('ssp')
        if ssp:
            validated_data['section'] = 'SSP ' + validated_data['section']
        if validated_data.get('stt').type == 'tribe':
            validated_data['section'] = 'Tribal ' + validated_data['section']
        data_file = DataFile.create_new_version(validated_data)
        # Determine the matching ClamAVFileScan for this DataFile.
        av_scan = ClamAVFileScan.objects.filter(
            file_name=data_file.original_filename,
            uploaded_by=data_file.user
        ).last()

        # Link the newly created DataFile to the relevant ClamAVFileScan.
        if av_scan is not None:
            av_scan.data_file = data_file
            av_scan.save()

        return data_file

    def update(self, instance, validated_data):
        """Throw an error if a user tries to update a data_file."""
        raise ImmutabilityError(instance, validated_data)

    def validate_file(self, file):
        """Perform all validation steps on a given file."""
        user = self.context.get('user')
        validate_file_extension(file.name)
        validate_file_infection(file, file.name, user)
        return file
