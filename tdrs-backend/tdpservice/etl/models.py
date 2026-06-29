"""Models for approved ETL pipeline execution and outputs."""

from django.conf import settings
from django.db import models

from tdpservice.data_files.models import DataFile


class ETLPipelineRun(models.Model):
    """One execution of one approved ETL pipeline."""

    class Status(models.TextChoices):
        """Pipeline run lifecycle states."""

        PENDING = "PENDING"
        RUNNING = "RUNNING"
        SUCCEEDED = "SUCCEEDED"
        FAILED = "FAILED"
        CANCELED = "CANCELED"

    class TriggerSource(models.TextChoices):
        """Where a pipeline run originated."""

        ADMIN = "ADMIN"
        SCHEDULED = "SCHEDULED"
        RETRY = "RETRY"

    pipeline_key = models.CharField(max_length=128)
    pipeline_version = models.CharField(max_length=32)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    parameters = models.JSONField(default=dict)
    output_scope = models.JSONField(default=dict)
    output_scope_key = models.CharField(max_length=64, editable=False)
    metadata = models.JSONField(default=dict)
    trigger_source = models.CharField(max_length=16, choices=TriggerSource.choices)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="etl_pipeline_runs",
        null=True,
        blank=True,
    )
    retry_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="retries",
        null=True,
        blank=True,
    )
    final_output = models.OneToOneField(
        "etl.ETLOutput",
        on_delete=models.SET_NULL,
        related_name="final_pipeline_run",
        null=True,
        blank=True,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata."""

        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["pipeline_key", "status"],
                name="etl_run_key_status_idx",
            ),
            models.Index(
                fields=["pipeline_key", "output_scope_key"],
                name="etl_run_scope_key_idx",
            ),
            models.Index(fields=["created_at"], name="etl_run_created_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("pipeline_key", "output_scope_key"),
                condition=models.Q(status__in=("PENDING", "RUNNING")),
                name="unique_active_etl_run_scope",
            )
        ]

    def __str__(self):
        """Return a concise run label."""
        return f"{self.pipeline_key} #{self.id} ({self.status})"


class ETLNodeRun(models.Model):
    """One node execution inside an ETL pipeline run."""

    class Status(models.TextChoices):
        """Node run lifecycle states."""

        PENDING = "PENDING"
        RUNNING = "RUNNING"
        SUCCEEDED = "SUCCEEDED"
        FAILED = "FAILED"

    pipeline_run = models.ForeignKey(
        ETLPipelineRun, on_delete=models.CASCADE, related_name="node_runs"
    )
    node_key = models.CharField(max_length=128)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    input_row_count = models.PositiveIntegerField(null=True, blank=True)
    output_row_count = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        """Model metadata."""

        ordering = ["pipeline_run_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=("pipeline_run", "node_key"),
                name="unique_etl_node_run_per_pipeline_run",
            )
        ]
        indexes = [
            models.Index(fields=["node_key", "status"], name="etl_node_key_status_idx")
        ]

    def __str__(self):
        """Return a concise node-run label."""
        return f"{self.pipeline_run_id}:{self.node_key} ({self.status})"


class ETLQAResult(models.Model):
    """Structured QA result emitted by a pipeline run."""

    class Status(models.TextChoices):
        """QA result status."""

        PASSED = "PASSED"
        WARNING = "WARNING"
        FAILED = "FAILED"

    pipeline_run = models.ForeignKey(
        ETLPipelineRun, on_delete=models.CASCADE, related_name="qa_results"
    )
    check_key = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=Status.choices)
    summary = models.TextField()
    result_payload = models.JSONField(default=dict)
    blocking = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model metadata."""

        ordering = ["pipeline_run_id", "id"]
        indexes = [
            models.Index(fields=["check_key", "status"], name="etl_qa_key_status_idx")
        ]

    def __str__(self):
        """Return a concise QA label."""
        return f"{self.check_key} ({self.status})"


class ETLOutput(models.Model):
    """Reference to a final pipeline output."""

    class OutputKind(models.TextChoices):
        """Supported output kinds."""

        TABLE = "TABLE"
        VIEW = "VIEW"
        FILE = "FILE"

    pipeline_run = models.ForeignKey(
        ETLPipelineRun, on_delete=models.CASCADE, related_name="outputs"
    )
    output_key = models.CharField(max_length=128)
    output_kind = models.CharField(max_length=16, choices=OutputKind.choices)
    reference = models.CharField(max_length=255)
    output_version = models.PositiveIntegerField(null=True, blank=True)
    row_count = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model metadata."""

        ordering = ["pipeline_run_id", "id"]
        indexes = [
            models.Index(
                fields=["output_key", "published"],
                name="etl_output_key_pub_idx",
            ),
            models.Index(
                fields=["output_key", "output_version"],
                name="etl_output_key_ver_idx",
            ),
        ]

    def __str__(self):
        """Return a concise output label."""
        return f"{self.output_key} v{self.output_version}"


class ETLIntermediateOutput(models.Model):
    """Run-scoped intermediate output used by downstream ETL nodes."""

    pipeline_run = models.ForeignKey(
        ETLPipelineRun,
        on_delete=models.CASCADE,
        related_name="intermediate_outputs",
    )
    output_key = models.CharField(max_length=128)
    payload = models.JSONField(default=dict)
    row_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata."""

        ordering = ["pipeline_run_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=("pipeline_run", "output_key"),
                name="unique_etl_intermediate_per_run",
            )
        ]
        indexes = [
            models.Index(
                fields=["output_key"],
                name="etl_intermediate_key_idx",
            )
        ]

    def __str__(self):
        """Return a concise intermediate-output label."""
        return f"{self.pipeline_run_id}:{self.output_key}"


class StatisticalWeight(models.Model):
    """Versioned statistical weight output rows."""

    fiscal_year = models.PositiveIntegerField()
    reporting_month = models.PositiveIntegerField()
    program = models.CharField(max_length=16, choices=DataFile.ProgramType.choices)
    section = models.CharField(max_length=16)
    stt_code = models.CharField(max_length=3)
    stratum = models.CharField(max_length=2)
    version = models.PositiveIntegerField()
    case_count = models.PositiveIntegerField()
    cases = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=12, decimal_places=4)
    pipeline_run = models.ForeignKey(
        ETLPipelineRun,
        on_delete=models.PROTECT,
        related_name="statistical_weights",
    )
    published_at = models.DateTimeField()
    retention_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Model metadata."""

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "fiscal_year",
                    "reporting_month",
                    "program",
                    "section",
                    "stt_code",
                    "stratum",
                    "version",
                ),
                name="unique_statistical_weight_version",
            )
        ]
        indexes = [
            models.Index(
                fields=["fiscal_year", "program", "section", "version"],
                name="etl_weight_scope_ver_idx",
            ),
            models.Index(
                fields=["retention_expires_at"],
                name="etl_weight_retention_idx",
            ),
        ]

    def __str__(self):
        """Return a concise weight label."""
        return (
            f"{self.program} FY{self.fiscal_year} {self.reporting_month} "
            f"{self.stt_code}/{self.stratum} v{self.version}"
        )
