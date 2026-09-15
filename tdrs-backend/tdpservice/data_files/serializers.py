"""Serialize stt data."""

import logging

from rest_framework import serializers

from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.models import DataFile, ReparseFileMeta, Section
from tdpservice.data_files.validators import validate_file_extension
from tdpservice.parsers.models import ParserError
from tdpservice.parsers.serializers import DataFileSummarySerializer
from tdpservice.stts.models import STT
from tdpservice.users.models import User

logger = logging.getLogger(__name__)


class ReparseFileMetaSerializer(serializers.ModelSerializer):
    """Serializer for ReparseFileMeta class."""

    class Meta:
        """Meta class."""

        model = ReparseFileMeta
        fields = [
            "finished",
            "success",
            "started_at",
            "finished_at",
        ]


class DataFileSerializer(serializers.ModelSerializer):
    """Serializer for Data files."""

    file = serializers.FileField(write_only=True)
    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    ssp = serializers.BooleanField(write_only=True)
    has_error = serializers.SerializerMethodField()
    summary = DataFileSummarySerializer(many=False, read_only=True)
    latest_reparse_file_meta = serializers.SerializerMethodField()
    program_type = serializers.CharField(read_only=True)

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
            "version",
            "s3_location",
            "s3_versioning_id",
            "has_error",
            "summary",
            "latest_reparse_file_meta",
            "is_program_audit",
            "program_type",
        ]

        read_only_fields = ("version", "program_type")

    def get_has_error(self, obj):
        """Return whether the file has an error."""
        # Use annotated value if available, otherwise fallback to query
        if hasattr(obj, "has_error"):
            return obj.has_error
        parser_errors = ParserError.objects.filter(file=obj.id, deprecated=False)
        return parser_errors.count() > 0

    def get_latest_reparse_file_meta(self, instance):
        """Return related reparse_file_metas, ordered by finished_at descending."""
        if hasattr(instance, "rfms") and len(instance.rfms) > 0:
            return ReparseFileMetaSerializer(
                instance.rfms[0], many=False, read_only=True
            ).data
        return None

    def create(self, validated_data):
        """Create a new entry with a new version number."""
        validated_data.pop("ssp")

        data_file = DataFile.create_new_version(validated_data)
        return data_file

    def to_representation(self, instance):
        """Project canonical classification through the legacy response fields."""
        representation = super().to_representation(instance)
        representation["section"] = instance.section_ref.name
        representation["program_type"] = instance.section_ref.program.code
        return representation

    def update(self, instance, validated_data):
        """Throw an error if a user tries to update a data_file."""
        raise ImmutabilityError(instance, validated_data)

    def validate(self, data):
        """Perform all validation steps on a given file."""
        file = data["file"] if "file" in data else None
        section = data["section"] if "section" in data else None

        if section and "ssp" in data and "stt" in data:
            if data["ssp"]:
                program_type = DataFile.ProgramType.SSP
            elif data["stt"].type == "tribe":
                program_type = DataFile.ProgramType.TRIBAL
            else:
                is_fra = Section.objects.filter(
                    program__code=DataFile.ProgramType.FRA,
                    name=section,
                ).exists()
                program_type = (
                    DataFile.ProgramType.FRA
                    if is_fra
                    else DataFile.ProgramType.TANF
                )

            try:
                section_ref = Section.from_legacy_values(program_type, section)
            except Section.DoesNotExist as error:
                raise serializers.ValidationError(
                    {
                        "section": (
                            "Section is not valid for the derived reporting program."
                        )
                    }
                ) from error

            if data.get("is_program_audit") and program_type not in {
                DataFile.ProgramType.TANF,
                DataFile.ProgramType.TRIBAL,
            }:
                raise serializers.ValidationError(
                    {
                        "is_program_audit": (
                            "Program audits require a TANF or Tribal TANF section."
                        )
                    }
                )

            user = self.context.get("user")
            if (
                program_type == DataFile.ProgramType.FRA
                and not user.has_fra_access
                and not user.is_ofa_sys_admin
            ):
                raise serializers.ValidationError({"section": "Section cannot be FRA"})

            if file:
                validate_file_extension(
                    file.name,
                    is_fra=program_type == DataFile.ProgramType.FRA,
                )

            data["program_type"] = program_type
            data["section_ref"] = section_ref

        return data

    def validate_section(self, section):
        """Return the compatibility section input for canonical validation."""
        return section
