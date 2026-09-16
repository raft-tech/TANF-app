"""Serialize stt data."""

import logging

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from tdpservice.data_files.enums import ProgramCode, SubmissionState
from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.models import DataFile, ReparseFileMeta, Section
from tdpservice.data_files.submission_lifecycle import allowed_next_states
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
    section = serializers.CharField()
    program_type = serializers.CharField(read_only=True)
    state_display = serializers.CharField(source="get_state_display", read_only=True)
    allowed_next_states = serializers.SerializerMethodField()

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
            "state",
            "state_display",
            "allowed_next_states",
        ]

        read_only_fields = ("version", "program_type", "state")

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

    @swagger_serializer_method(
        serializer_or_field=serializers.ListField(
            child=serializers.ChoiceField(choices=SubmissionState.choices),
            read_only=True,
        )
    )
    def get_allowed_next_states(self, instance: DataFile) -> list[str]:
        """Return valid lifecycle transitions in a stable order."""
        try:
            allowed_states = allowed_next_states(instance.state)
        except (KeyError, TypeError, ValueError):
            logger.warning(
                "DataFile has an unknown submission lifecycle state.",
                extra={
                    "data_file_id": instance.pk,
                    "state": instance.state,
                },
            )
            return []

        return [state.value for state in SubmissionState if state in allowed_states]

    def create(self, validated_data):
        """Create a new entry with a new version number."""
        validated_data.pop("ssp")

        data_file = DataFile.create_new_version(validated_data)
        return data_file

    def to_representation(self, instance):
        """Project canonical classification through the legacy response fields."""
        representation = super().to_representation(instance)
        representation["section"] = instance.section.name
        representation["program_type"] = instance.section.program.code
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
                program_type = ProgramCode.SSP
            elif data["stt"].type == "tribe":
                program_type = ProgramCode.TRIBAL
            else:
                is_fra = Section.objects.filter(
                    program__code=ProgramCode.FRA,
                    name=section,
                ).exists()
                program_type = (
                    ProgramCode.FRA
                    if is_fra
                    else ProgramCode.TANF
                )

            try:
                section = Section.objects.select_related("program").get(
                    program__code=program_type,
                    name=section,
                )
            except Section.DoesNotExist as error:
                raise serializers.ValidationError(
                    {
                        "section": (
                            "Section is not valid for the derived reporting program."
                        )
                    }
                ) from error

            if data.get("is_program_audit") and program_type not in {
                ProgramCode.TANF,
                ProgramCode.TRIBAL,
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
                program_type == ProgramCode.FRA
                and not user.has_fra_access
                and not user.is_ofa_sys_admin
            ):
                raise serializers.ValidationError({"section": "Section cannot be FRA"})

            if file:
                validate_file_extension(
                    file.name,
                    is_fra=program_type == ProgramCode.FRA,
                )

            data["section"] = section

        return data

    def validate_section(self, section):
        """Return the compatibility section input for canonical validation."""
        return section
