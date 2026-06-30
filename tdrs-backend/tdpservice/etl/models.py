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
        "etl.ETLArtifact",
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

        verbose_name = "ETL Pipeline"
        verbose_name_plural = "ETL Pipelines"
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

        verbose_name = "ETL Node Run"
        verbose_name_plural = "ETL Node Runs"
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

        verbose_name = "ETL QA Result"
        verbose_name_plural = "ETL QA Results"
        ordering = ["pipeline_run_id", "id"]
        indexes = [
            models.Index(fields=["check_key", "status"], name="etl_qa_key_status_idx")
        ]

    def __str__(self):
        """Return a concise QA label."""
        return f"{self.check_key} ({self.status})"


class ETLArtifact(models.Model):
    """Run-scoped artifact produced and consumed by ETL nodes."""

    class ArtifactRole(models.TextChoices):
        """Artifact roles within a pipeline run."""

        INTERMEDIATE = "INTERMEDIATE"
        FINAL = "FINAL"

    class ArtifactKind(models.TextChoices):
        """Logical artifact shapes supported by ETL pipelines."""

        DATASET = "DATASET"
        FILE = "FILE"
        SCALAR = "SCALAR"

    class StorageKind(models.TextChoices):
        """Physical storage backends for ETL artifacts."""

        POSTGRES_TABLE = "POSTGRES_TABLE"
        OBJECT = "OBJECT"
        INLINE_JSON = "INLINE_JSON"

    pipeline_run = models.ForeignKey(
        ETLPipelineRun,
        on_delete=models.CASCADE,
        related_name="artifacts",
    )
    key = models.CharField(max_length=128)
    artifact_role = models.CharField(
        max_length=16,
        choices=ArtifactRole.choices,
        default=ArtifactRole.INTERMEDIATE,
    )
    artifact_kind = models.CharField(max_length=16, choices=ArtifactKind.choices)
    storage_kind = models.CharField(max_length=32, choices=StorageKind.choices)
    reference = models.CharField(max_length=255)
    schema_key = models.CharField(max_length=128)
    schema_version = models.PositiveIntegerField(default=1)
    version = models.PositiveIntegerField(null=True, blank=True)
    row_count = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata."""

        verbose_name = "ETL Artifact"
        verbose_name_plural = "ETL Artifacts"
        ordering = ["pipeline_run_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=("pipeline_run", "key"),
                name="unique_etl_artifact_per_run",
            )
        ]
        indexes = [
            models.Index(
                fields=["key"],
                name="etl_artifact_key_idx",
            ),
            models.Index(
                fields=["key", "artifact_role"],
                name="etl_artifact_key_role_idx",
            ),
            models.Index(
                fields=["artifact_kind", "storage_kind"],
                name="etl_artifact_kind_store_idx",
            ),
            models.Index(
                fields=["artifact_role", "published"],
                name="etl_artifact_role_pub_idx",
            ),
        ]

    def __str__(self):
        """Return a concise artifact label."""
        return f"{self.pipeline_run_id}:{self.key} ({self.artifact_role})"


class StatisticalWeightsActiveFamilyCount(models.Model):
    """Run-scoped s1 active-family counts for statistical weights."""

    pipeline_run = models.ForeignKey(
        ETLPipelineRun,
        on_delete=models.CASCADE,
        related_name="statistical_weight_active_family_counts",
    )
    stt_code = models.CharField(max_length=3)
    reporting_month = models.PositiveIntegerField()
    stratum = models.CharField(max_length=2)
    case_count = models.PositiveIntegerField()

    class Meta:
        """Model metadata."""

        verbose_name = "Statistical Weights Active Family Count"
        verbose_name_plural = "Statistical Weights Active Family Counts"
        ordering = ["pipeline_run_id", "stt_code", "reporting_month", "stratum"]
        constraints = [
            models.UniqueConstraint(
                fields=("pipeline_run", "stt_code", "reporting_month", "stratum"),
                name="unique_sw_active_family_count",
            )
        ]
        indexes = [
            models.Index(
                fields=["pipeline_run", "reporting_month"],
                name="sw_s1_run_month_idx",
            )
        ]

    def __str__(self):
        """Return a concise s1 row label."""
        return (
            f"{self.pipeline_run_id}:{self.stt_code}/"
            f"{self.reporting_month}/{self.stratum}"
        )


class StatisticalWeightsAggregateCaseCount(models.Model):
    """Run-scoped s3 aggregate case counts for statistical weights."""

    pipeline_run = models.ForeignKey(
        ETLPipelineRun,
        on_delete=models.CASCADE,
        related_name="statistical_weight_aggregate_case_counts",
    )
    stt_code = models.CharField(max_length=3)
    reporting_month = models.PositiveIntegerField()
    case_count = models.PositiveIntegerField()

    class Meta:
        """Model metadata."""

        verbose_name = "Statistical Weights Aggregate Case Count"
        verbose_name_plural = "Statistical Weights Aggregate Case Counts"
        ordering = ["pipeline_run_id", "stt_code", "reporting_month"]
        constraints = [
            models.UniqueConstraint(
                fields=("pipeline_run", "stt_code", "reporting_month"),
                name="unique_sw_aggregate_case_count",
            )
        ]
        indexes = [
            models.Index(
                fields=["pipeline_run", "reporting_month"],
                name="sw_s3_run_month_idx",
            )
        ]

    def __str__(self):
        """Return a concise s3 row label."""
        return f"{self.pipeline_run_id}:{self.stt_code}/{self.reporting_month}"


class StatisticalWeightsStratumCaseCount(models.Model):
    """Run-scoped s4 stratum case counts for statistical weights."""

    pipeline_run = models.ForeignKey(
        ETLPipelineRun,
        on_delete=models.CASCADE,
        related_name="statistical_weight_stratum_case_counts",
    )
    stt_code = models.CharField(max_length=3)
    reporting_month = models.PositiveIntegerField()
    stratum = models.CharField(max_length=2)
    cases = models.PositiveIntegerField()

    class Meta:
        """Model metadata."""

        verbose_name = "Statistical Weights Stratum Case Count"
        verbose_name_plural = "Statistical Weights Stratum Case Counts"
        ordering = ["pipeline_run_id", "stt_code", "reporting_month", "stratum"]
        constraints = [
            models.UniqueConstraint(
                fields=("pipeline_run", "stt_code", "reporting_month", "stratum"),
                name="unique_sw_stratum_case_count",
            )
        ]
        indexes = [
            models.Index(
                fields=["pipeline_run", "reporting_month"],
                name="sw_s4_run_month_idx",
            )
        ]

    def __str__(self):
        """Return a concise s4 row label."""
        return (
            f"{self.pipeline_run_id}:{self.stt_code}/"
            f"{self.reporting_month}/{self.stratum}"
        )


class StatisticalWeightCandidate(models.Model):
    """Run-scoped candidate statistical weight rows before publication."""

    pipeline_run = models.ForeignKey(
        ETLPipelineRun,
        on_delete=models.CASCADE,
        related_name="statistical_weight_candidates",
    )
    fiscal_year = models.PositiveIntegerField()
    reporting_month = models.PositiveIntegerField()
    program = models.CharField(max_length=16, choices=DataFile.ProgramType.choices)
    section = models.CharField(max_length=16)
    stt_code = models.CharField(max_length=3)
    stratum = models.CharField(max_length=2)
    case_count = models.PositiveIntegerField()
    cases = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        """Model metadata."""

        verbose_name = "Statistical Weight Candidate"
        verbose_name_plural = "Statistical Weight Candidates"
        ordering = ["pipeline_run_id", "stt_code", "reporting_month", "stratum"]
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "pipeline_run",
                    "fiscal_year",
                    "reporting_month",
                    "program",
                    "section",
                    "stt_code",
                    "stratum",
                ),
                name="unique_statistical_weight_candidate",
            )
        ]
        indexes = [
            models.Index(
                fields=["pipeline_run", "program", "section"],
                name="sw_candidate_scope_idx",
            )
        ]

    def __str__(self):
        """Return a concise candidate label."""
        return (
            f"{self.pipeline_run_id}:{self.program} FY{self.fiscal_year} "
            f"{self.reporting_month} {self.stt_code}/{self.stratum}"
        )


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

        verbose_name = "Statistical Weight"
        verbose_name_plural = "Statistical Weights"
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
