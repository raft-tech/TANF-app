"""Serializers for ETL pipeline APIs."""

from rest_framework import serializers

from tdpservice.etl.models import ETLNodeRun, ETLOutput, ETLPipelineRun, ETLQAResult
from tdpservice.etl.registry import get_pipeline_definition, list_pipeline_definitions
from tdpservice.etl.runner import PipelineValidationError, validate_run_parameters


class PipelineDefinitionSerializer(serializers.Serializer):
    """Serialize a code-defined pipeline definition."""

    key = serializers.CharField()
    version = serializers.CharField()
    display_name = serializers.CharField()
    description = serializers.CharField()
    allowed_parameters = serializers.JSONField()
    schedule = serializers.JSONField(allow_null=True)
    nodes = serializers.JSONField()

    @classmethod
    def from_registry(cls, **kwargs):
        """Return a serializer over registered pipeline definitions."""
        definitions = [
            definition.serialize() for definition in list_pipeline_definitions()
        ]
        return cls(definitions, **kwargs)


class ETLNodeRunSerializer(serializers.ModelSerializer):
    """Serialize node run status."""

    class Meta:
        """Serializer metadata."""

        model = ETLNodeRun
        fields = [
            "id",
            "node_key",
            "status",
            "dependency_status",
            "started_at",
            "finished_at",
            "input_row_count",
            "output_row_count",
            "error_message",
            "metadata",
        ]


class ETLQAResultSerializer(serializers.ModelSerializer):
    """Serialize persisted QA checks."""

    class Meta:
        """Serializer metadata."""

        model = ETLQAResult
        fields = [
            "id",
            "check_key",
            "status",
            "summary",
            "result_payload",
            "blocking",
            "created_at",
        ]


class ETLOutputSerializer(serializers.ModelSerializer):
    """Serialize output references."""

    class Meta:
        """Serializer metadata."""

        model = ETLOutput
        fields = [
            "id",
            "output_key",
            "output_kind",
            "reference",
            "output_version",
            "row_count",
            "published",
            "metadata",
            "created_at",
        ]


class ETLPipelineRunSerializer(serializers.ModelSerializer):
    """Serialize pipeline run history with node, QA, and output status."""

    node_runs = ETLNodeRunSerializer(many=True, read_only=True)
    qa_results = ETLQAResultSerializer(many=True, read_only=True)
    outputs = ETLOutputSerializer(many=True, read_only=True)

    class Meta:
        """Serializer metadata."""

        model = ETLPipelineRun
        fields = [
            "id",
            "pipeline_key",
            "pipeline_version",
            "status",
            "parameters",
            "output_scope",
            "metadata",
            "trigger_source",
            "triggered_by",
            "retry_of",
            "started_at",
            "finished_at",
            "error_message",
            "created_at",
            "updated_at",
            "node_runs",
            "qa_results",
            "outputs",
        ]
        read_only_fields = fields


class ETLPipelineRunCreateSerializer(serializers.Serializer):
    """Validate admin-created pipeline run requests."""

    pipeline_key = serializers.CharField()
    parameters = serializers.JSONField(default=dict)

    def validate(self, attrs):
        """Validate the requested pipeline key and parameters."""
        try:
            definition = get_pipeline_definition(attrs["pipeline_key"])
        except KeyError as exc:
            raise serializers.ValidationError({"pipeline_key": str(exc)}) from exc

        try:
            attrs["parameters"] = validate_run_parameters(
                definition,
                attrs.get("parameters", {}),
            )
        except PipelineValidationError as exc:
            raise serializers.ValidationError({"parameters": str(exc)}) from exc

        return attrs
