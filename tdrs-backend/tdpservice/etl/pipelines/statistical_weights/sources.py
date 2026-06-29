"""Source selection for statistical weights."""

from tdpservice.data_files.models import DataFile
from tdpservice.etl.pipelines.sources import DataFileSource, DataFileSourceSnapshot
from tdpservice.etl.pipelines.statistical_weights.adapters import adapter_for_program


class StatisticalWeightsSources:
    """Declare and snapshot statistical weights DataFile sources."""

    def __init__(
        self,
        *,
        source_keys: dict[str, str],
        datafile_snapshot: DataFileSourceSnapshot | None = None,
    ):
        """Initialize source selection with the shared DataFile snapshot helper."""
        self.source_keys = source_keys
        self.datafile_snapshot = datafile_snapshot or DataFileSourceSnapshot()

    def datafile_sources(self, program_type: str) -> tuple[DataFileSource, ...]:
        """Return DataFile source declarations for one weights program."""
        adapter = adapter_for_program(program_type)
        return (
            DataFileSource(
                key=self.source_keys["active"],
                program_type=adapter.program_type,
                section=DataFile.Section.ACTIVE_CASE_DATA,
            ),
            DataFileSource(
                key=self.source_keys["aggregate"],
                program_type=adapter.program_type,
                section=DataFile.Section.AGGREGATE_DATA,
            ),
            DataFileSource(
                key=self.source_keys["stratum"],
                program_type=adapter.program_type,
                section=DataFile.Section.STRATUM_DATA,
            ),
        )

    def snapshot_source_datafile_ids(
        self,
        fiscal_year: int,
        program_type: str,
    ) -> dict[str, list[int]]:
        """Return a fresh source DataFile snapshot for one weights run."""
        return self.datafile_snapshot.build_snapshot(
            fiscal_year=fiscal_year,
            sources=self.datafile_sources(program_type),
        )

    def source_datafile_ids(self, context) -> dict[str, list[int]]:
        """Return a run's source DataFile snapshot, creating it once when needed."""
        return self.datafile_snapshot.snapshot(
            context.pipeline_run,
            fiscal_year=int(context.parameters["fiscal_year"]),
            sources=self.datafile_sources(context.parameters["program"]),
        )
