"""Unit tests for ParsingService and ParseResult."""

import io
import uuid

from django.db.utils import DatabaseError

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import (
    DataFile,
    DataFileStateTransition,
    Program,
    ReparseFileMeta,
    Section,
    ShadowDataFile,
    create_or_update_shadow_data_file,
)
from tdpservice.data_files.submission_lifecycle import StaleParseOwnership
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ParserErrorCategoryChoices,
    ShadowDataFileSummary,
)
from tdpservice.parsers.parser_classes.tdr_parser import TanfDataReportParser
from tdpservice.parsers.service import (
    ParseResult,
    ParsingService,
    PythonParserEngine,
    _calculate_total_records,
    _finalize_reparse,
    _get_summary_status,
    _parser_models_for_mode,
    _program_code,
    _section_name,
    _shadow_record_model,
    _uses_shadow_table,
    should_send_reparse_notification,
    update_dfs,
)
from tdpservice.parsers.util import DecoderUnknownException
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.search_indexes.models.shadow import ShadowTANF_T1
from tdpservice.search_indexes.models.tanf import TANF_T1


class DummyHandler:
    """Logger handler stub to capture rollover calls."""

    def __init__(self):
        self.called = False
        self.level = 0

    def doRollover(self, data_file):
        """Record rollover invocation."""
        self.called = True

    def handle(self, record):
        """No-op handler for logger internals."""
        return True


class DummyParser:
    """Parser stub used for flow control tests."""

    def __init__(self, exc=None):
        self.exc = exc
        self.called = False

    def parse_and_validate(self):
        """Invoke a configured exception or no-op."""
        self.called = True
        if self.exc is not None:
            raise self.exc


DEFAULT_FILENAMES = {
    Section.Name.ACTIVE_CASE_DATA: "ADS.E2J.FTP1.TS72",
    Section.Name.CLOSED_CASE_DATA: "ADS.E2J.FTP2.TS72",
    Section.Name.AGGREGATE_DATA: "ADS.E2J.FTP3.TS72",
    Section.Name.STRATUM_DATA: "ADS.E2J.FTP4.TS72",
    Section.Name.FRA_WORK_OUTCOMES: "ADS.FRA.FTP1.TS72",
    Section.Name.FRA_SECONDARY_SCHOOL_ATTAINMENT: "ADS.FRA.FTP2.TS72",
    Section.Name.FRA_SUPPLEMENTAL_WORK_OUTCOMES: "ADS.FRA.FTP3.TS72",
}


def ensure_stt_filenames(stt):
    """Set default STT filenames when missing to unblock parse logging."""
    if not stt.filenames:
        stt.filenames = DEFAULT_FILENAMES.copy()
        stt.save(update_fields=["filenames"])


def setup_service_mocks(monkeypatch, dfs=None):
    """Patch common dependencies for ParsingService tests."""
    from tdpservice.parsers import service

    handlers = [DummyHandler(), DummyHandler(), DummyHandler()]
    monkeypatch.setattr(service.logger, "handlers", handlers, raising=False)
    monkeypatch.setattr(service, "change_log_filename", lambda *a, **k: None)

    def fake_update_dfs(dfs, data_file, **kwargs):
        dfs.status = DataFileSummary.Status.ACCEPTED
        dfs.save()

    monkeypatch.setattr(service, "update_dfs", fake_update_dfs)
    monkeypatch.setattr(service, "set_error_report", lambda *a, **k: None)
    if dfs is not None:
        monkeypatch.setattr(
            service.DataFileSummary.objects, "create", lambda **kwargs: dfs
        )

    class DummyReport:
        def generate(self):
            return io.BytesIO(b"report")

    monkeypatch.setattr(
        service.ErrorReportFactory,
        "get_error_report_generator",
        lambda *a, **k: DummyReport(),
    )
    return handlers


@pytest.mark.django_db
class TestParseResult:
    """Tests for ParseResult dataclass and serialization."""

    def test_to_dict_serialization(self, data_analyst):
        """Ensure ParseResult correctly converts to lightweight dictionary."""
        datafile = DataFileFactory(stt=data_analyst.stt)
        dfs = DataFileSummary.objects.create(
            datafile=datafile, status=DataFileSummary.Status.ACCEPTED
        )
        result = ParseResult(
            success=True,
            data_file=datafile,
            summary=dfs,
            status=dfs.status,
            error_message=None,
            total_records_processed=100,
            total_errors_generated=2,
        )
        dict_val = result.to_dict()
        assert dict_val == {
            "success": True,
            "data_file_id": datafile.id,
            "summary_id": dfs.id,
            "status": DataFileSummary.Status.ACCEPTED,
            "error_message": None,
            "total_records_processed": 100,
            "total_errors_generated": 2,
        }

    def test_to_dict_empty(self):
        """Ensure ParseResult defaults convert to dictionary gracefully."""
        result = ParseResult(success=False, error_message="Failed early")
        dict_val = result.to_dict()
        assert dict_val == {
            "success": False,
            "data_file_id": None,
            "summary_id": None,
            "status": None,
            "error_message": "Failed early",
            "total_records_processed": 0,
            "total_errors_generated": 0,
        }


@pytest.mark.django_db
class TestParsingServicePreconditions:
    """Tests for ParsingService data fetching and precondition checks."""

    def test_fetch_data_file(self, data_analyst):
        """Return the provided DataFile instance."""
        datafile = DataFileFactory(stt=data_analyst.stt)
        service = ParsingService(data_file=datafile)
        assert service.fetch_data_file() is datafile

    def test_fetch_data_file_missing_instance(self):
        """Raise ValueError when data_file is not provided."""
        with pytest.raises(ValueError, match="data_file must be provided"):
            ParsingService(data_file=None)

    def test_validate_preconditions_missing_file_content(self, data_analyst):
        """Raise ValueError when DataFile has no file attached."""
        datafile = DataFileFactory(stt=data_analyst.stt, file=None)
        service = ParsingService(data_file=datafile)
        with pytest.raises(ValueError, match="does not have an associated file"):
            service.validate_preconditions()

    @pytest.mark.parametrize(
        "invalid_state",
        [
            SubmissionState.UPLOADED,
            SubmissionState.VIRUS_SCAN_STARTED,
            SubmissionState.VIRUS_SCAN_FAILED,
            SubmissionState.CANCELED,
            SubmissionState.COMPLETED,
            SubmissionState.STUCK,
        ],
    )
    def test_validate_preconditions_invalid_state(self, data_analyst, invalid_state):
        """Raise ValueError when DataFile is in an unparseable state."""
        datafile = DataFileFactory(stt=data_analyst.stt, state=invalid_state)
        service = ParsingService(data_file=datafile)
        with pytest.raises(ValueError, match="Cannot queue parsing"):
            service.validate_preconditions()

    @pytest.mark.parametrize(
        "valid_state",
        [
            SubmissionState.VIRUS_SCAN_COMPLETED,
            SubmissionState.REPARSE_REQUESTED,
            SubmissionState.PARSE_FAILED,
            SubmissionState.PARSE_STARTED,
        ],
    )
    def test_validate_preconditions_valid_state(self, data_analyst, valid_state):
        """Pass validation when DataFile is in a parse-eligible state."""
        datafile = DataFileFactory(stt=data_analyst.stt, state=valid_state)
        service = ParsingService(data_file=datafile)
        # Should not raise
        service.validate_preconditions()

    def test_validate_preconditions_stale_token_mismatch(self, data_analyst):
        """Raise StaleParseOwnership when active token does not match provided token."""
        active_token = uuid.uuid4()
        other_token = uuid.uuid4()
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            state=SubmissionState.PARSE_STARTED,
            current_parse_token=active_token,
        )
        service = ParsingService(data_file=datafile, parse_token=other_token)
        with pytest.raises(StaleParseOwnership, match="does not match provided token"):
            service.validate_preconditions()


@pytest.mark.django_db
class TestParsingServiceParserSelection:
    """Tests for parser selection wrapping ParserFactory."""

    def test_get_parser_returns_tanf_parser(self, data_analyst):
        """Return TanfDataReportParser for TANF data files."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            program_type=Program.Code.TANF,
            section=Section.Name.ACTIVE_CASE_DATA,
        )
        service = ParsingService(data_file=datafile)
        parser = service.get_parser()
        assert isinstance(parser, TanfDataReportParser)


@pytest.mark.django_db
class TestParsingServiceExecution:
    """Tests for core parse execution and ParseResult structured outcomes."""

    def test_parse_success_returns_structured_result(self, monkeypatch, data_analyst):
        """Return success ParseResult with summary and transition records."""
        datafile = DataFileFactory(
            stt=data_analyst.stt, version=4, state=SubmissionState.VIRUS_SCAN_COMPLETED
        )
        ensure_stt_filenames(datafile.stt)
        dfs = DataFileSummary.objects.create(
            datafile=datafile, status=DataFileSummary.Status.PENDING
        )
        handlers = setup_service_mocks(monkeypatch, dfs=dfs)
        dummy_parser = DummyParser()

        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )

        captured = {}

        def fake_send(dfs, recipients, is_reprocessed=False):
            captured["recipients"] = list(recipients)

        monkeypatch.setattr(service, "send_data_submitted_email", fake_send)

        event_id = uuid.uuid4()
        ps = ParsingService(data_file=datafile, event_id=event_id)
        result = ps.run()

        assert isinstance(result, ParseResult)
        assert result.success is True
        assert result.data_file.id == datafile.id
        assert result.summary == dfs
        assert result.status == DataFileSummary.Status.ACCEPTED
        assert result.error_message is None
        assert dummy_parser.called is True
        assert data_analyst.username in captured["recipients"]
        assert handlers[2].called is True

        datafile.refresh_from_db()
        assert datafile.state == SubmissionState.PARSE_COMPLETED
        transitions = DataFileStateTransition.objects.for_object(datafile)
        assert transitions.count() == 2
        assert {transition.event_id for transition in transitions} == {event_id}

    def test_parse_alias_matches_run(self, monkeypatch, data_analyst):
        """Ensure parse() method delegates to run()."""
        datafile = DataFileFactory(
            stt=data_analyst.stt, version=4, state=SubmissionState.VIRUS_SCAN_COMPLETED
        )
        ensure_stt_filenames(datafile.stt)
        dfs = DataFileSummary.objects.create(
            datafile=datafile, status=DataFileSummary.Status.PENDING
        )
        setup_service_mocks(monkeypatch, dfs=dfs)
        dummy_parser = DummyParser()

        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )
        monkeypatch.setattr(service, "send_data_submitted_email", lambda *a, **k: None)

        ps = ParsingService(data_file=datafile)
        result = ps.parse()

        assert result.success is True
        assert dummy_parser.called is True

    def test_parse_decoder_unknown_returns_failed_result(
        self, monkeypatch, data_analyst
    ):
        """Return failure ParseResult on DecoderUnknownException."""
        datafile = DataFileFactory(
            stt=data_analyst.stt, version=1, state=SubmissionState.VIRUS_SCAN_COMPLETED
        )
        ensure_stt_filenames(datafile.stt)
        setup_service_mocks(monkeypatch)

        dummy_parser = DummyParser(exc=DecoderUnknownException("unknown encoding"))
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )

        ps = ParsingService(data_file=datafile)
        result = ps.run()

        assert result.success is False
        assert "unknown encoding" in result.error_message
        datafile.refresh_from_db()
        assert datafile.state == SubmissionState.PARSE_FAILED

    def test_parse_database_error_returns_failed_result(
        self, monkeypatch, data_analyst
    ):
        """Return failure ParseResult on DatabaseError."""
        datafile = DataFileFactory(
            stt=data_analyst.stt, version=2, state=SubmissionState.VIRUS_SCAN_COMPLETED
        )
        ensure_stt_filenames(datafile.stt)
        setup_service_mocks(monkeypatch)

        dummy_parser = DummyParser(exc=DatabaseError("db query failed"))
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )

        ps = ParsingService(data_file=datafile)
        result = ps.run()

        assert result.success is False
        assert "db query failed" in result.error_message
        datafile.refresh_from_db()
        assert datafile.state == SubmissionState.PARSE_FAILED

    def test_parse_unexpected_exception_creates_error_and_returns_failed_result(
        self, monkeypatch, data_analyst
    ):
        """Return failure ParseResult and persist user-facing error on unexpected error."""
        datafile = DataFileFactory(
            stt=data_analyst.stt, version=3, state=SubmissionState.VIRUS_SCAN_COMPLETED
        )
        ensure_stt_filenames(datafile.stt)
        setup_service_mocks(monkeypatch)

        dummy_parser = DummyParser(exc=RuntimeError("unexpected parser crash"))
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )

        ps = ParsingService(data_file=datafile)
        result = ps.run()

        assert result.success is False
        assert "unexpected parser crash" in result.error_message
        datafile.refresh_from_db()
        assert datafile.state == SubmissionState.PARSE_FAILED
        assert ParserError.objects.filter(file=datafile).exists()

    def test_parse_records_execution_metadata_on_success(
        self, monkeypatch, data_analyst
    ):
        """Verify execution metadata is recorded on the state transition on successful parse."""
        datafile = DataFileFactory(
            stt=data_analyst.stt, version=4, state=SubmissionState.VIRUS_SCAN_COMPLETED
        )
        ensure_stt_filenames(datafile.stt)
        setup_service_mocks(monkeypatch)

        dummy_parser = DummyParser()
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )
        monkeypatch.setattr(service, "send_data_submitted_email", lambda *a, **k: None)

        ps = ParsingService(data_file=datafile)
        result = ps.run()

        assert result.success is True
        transitions = DataFileStateTransition.objects.for_object(datafile)
        last_transition = transitions.first()
        assert last_transition is not None
        assert last_transition.metadata.get("parser_class") == "DummyParser"
        assert last_transition.metadata.get("execution_duration_ms") is not None
        assert last_transition.metadata.get("execution_duration_ms") >= 0
        assert last_transition.metadata.get("total_records_processed") == 0
        assert last_transition.metadata.get("total_errors_generated") == 0

    def test_parse_records_execution_metadata_on_failure(
        self, monkeypatch, data_analyst
    ):
        """Verify execution metadata is recorded on the state transition on parse failure."""
        datafile = DataFileFactory(
            stt=data_analyst.stt, version=5, state=SubmissionState.VIRUS_SCAN_COMPLETED
        )
        ensure_stt_filenames(datafile.stt)
        setup_service_mocks(monkeypatch)

        dummy_parser = DummyParser(exc=RuntimeError("unexpected crash"))
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )

        ps = ParsingService(data_file=datafile)
        result = ps.run()

        assert result.success is False
        transitions = DataFileStateTransition.objects.for_object(datafile)
        last_transition = transitions.first()
        assert last_transition is not None
        assert last_transition.metadata.get("parser_class") == "DummyParser"
        assert last_transition.metadata.get("execution_duration_ms") is not None
        assert last_transition.metadata.get("execution_duration_ms") >= 0
        assert last_transition.metadata.get("total_records_processed") == 0
        assert last_transition.metadata.get("total_errors_generated") == 0

    def test_parse_records_execution_metadata_on_shadow_data_file_success(
        self, monkeypatch, data_analyst
    ):
        """Verify execution metadata is recorded on ShadowDataFile state transition on success."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=8,
            state=SubmissionState.VIRUS_SCAN_COMPLETED,
            section=Section.Name.AGGREGATE_DATA,
        )
        shadow_datafile = create_or_update_shadow_data_file(datafile)
        ensure_stt_filenames(datafile.stt)
        setup_service_mocks(monkeypatch)

        dummy_parser = DummyParser()
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )

        ps = ParsingService(data_file=shadow_datafile)
        result = ps.run()

        assert result.success is True
        transitions = DataFileStateTransition.objects.for_object(shadow_datafile)
        last_transition = transitions.first()
        assert last_transition is not None
        assert last_transition.content_object == shadow_datafile
        assert last_transition.metadata.get("parser_class") == "DummyParser"
        assert last_transition.metadata.get("execution_duration_ms") is not None
        assert last_transition.metadata.get("execution_duration_ms") >= 0
        assert last_transition.metadata.get("total_records_processed") == 0
        assert last_transition.metadata.get("total_errors_generated") == 0
        assert last_transition.metadata.get("section") == Section.Name.AGGREGATE_DATA

    def test_parse_records_execution_metadata_on_shadow_data_file_failure(
        self, monkeypatch, data_analyst
    ):
        """Verify execution metadata is recorded on ShadowDataFile state transition on failure."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=9,
            state=SubmissionState.VIRUS_SCAN_COMPLETED,
            section=Section.Name.ACTIVE_CASE_DATA,
        )
        shadow_datafile = create_or_update_shadow_data_file(datafile)
        ensure_stt_filenames(datafile.stt)
        setup_service_mocks(monkeypatch)

        dummy_parser = DummyParser(exc=RuntimeError("shadow parse failed"))
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )

        ps = ParsingService(data_file=shadow_datafile)
        result = ps.run()

        assert result.success is False
        transitions = DataFileStateTransition.objects.for_object(shadow_datafile)
        last_transition = transitions.first()
        assert last_transition is not None
        assert last_transition.content_object == shadow_datafile
        assert last_transition.metadata.get("parser_class") == "DummyParser"
        assert last_transition.metadata.get("execution_duration_ms") is not None
        assert last_transition.metadata.get("execution_duration_ms") >= 0
        assert last_transition.metadata.get("total_records_processed") == 0
        assert last_transition.metadata.get("total_errors_generated") == 0
        assert last_transition.metadata.get("section") == Section.Name.ACTIVE_CASE_DATA

    def test_post_parse_production_success(self, data_analyst):
        """Verify post_parse finalizes production data file summary and transitions state."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=10,
            state=SubmissionState.VIRUS_SCAN_COMPLETED,
        )
        ps = ParsingService(data_file=datafile)
        ps.post_parse(table_mode="go-only")

        datafile.refresh_from_db()
        dfs = DataFileSummary.objects.get(datafile=datafile)
        assert dfs.status == DataFileSummary.Status.ACCEPTED
        assert datafile.state == SubmissionState.PARSE_COMPLETED

    def test_post_parse_production_error(self, data_analyst):
        """Verify post_parse handles parse_error for production data file."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=11,
            state=SubmissionState.VIRUS_SCAN_COMPLETED,
        )
        ps = ParsingService(data_file=datafile)
        ps.post_parse(parse_error="Go fatal error", table_mode="go-only")

        datafile.refresh_from_db()
        dfs = DataFileSummary.objects.get(datafile=datafile)
        assert dfs.status == DataFileSummary.Status.REJECTED
        assert datafile.state == SubmissionState.PARSE_FAILED

    def test_uses_shadow_table_property(self, data_analyst):
        """Verify uses_shadow_table property correctly distinguishes production vs shadow."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=12)
        shadow_datafile = create_or_update_shadow_data_file(datafile)

        prod_service = ParsingService(data_file=datafile)
        assert prod_service.uses_shadow_table is False

        shadow_service = ParsingService(data_file=shadow_datafile)
        assert shadow_service.uses_shadow_table is True

    def test_for_post_parse_factory(self, data_analyst):
        """Verify for_post_parse constructs ParsingService with expected model family."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=13)
        shadow_datafile = create_or_update_shadow_data_file(datafile)

        prod_service = ParsingService.for_post_parse(
            data_file_id=datafile.id,
            table_mode="go-only",
            reparse_id=1,
            parse_token="test-token",
        )
        assert isinstance(prod_service.data_file, DataFile)
        assert prod_service.data_file.id == datafile.id
        assert prod_service.uses_shadow_table is False
        assert prod_service.parse_token == "test-token"

        shadow_service = ParsingService.for_post_parse(
            data_file_id=shadow_datafile.id,
            table_mode="go-shadow",
            reparse_id=2,
            parse_token="shadow-token",
        )
        assert isinstance(shadow_service.data_file, ShadowDataFile)
        assert shadow_service.data_file.id == shadow_datafile.id
        assert shadow_service.uses_shadow_table is True

    def test_python_parser_engine(self, monkeypatch, data_analyst):
        """Verify PythonParserEngine constructs parser and executes parsing."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=14)
        dummy_parser = DummyParser()
        from tdpservice.parsers import service
        from tdpservice.parsers.service import PythonParserEngine

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )

        engine = PythonParserEngine(data_file=datafile)
        parser = engine.get_parser()
        assert parser is dummy_parser

        result = engine.execute()
        assert result is dummy_parser
        assert dummy_parser.called is True

    def test_parsing_service_scheduling_delegates(self, monkeypatch, data_analyst):
        """Verify ParsingService.schedule claims parse and routes dispatch."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=15,
            state=SubmissionState.VIRUS_SCAN_COMPLETED,
        )
        calls = []

        from tdpservice.scheduling import parser_task
        monkeypatch.setattr(
            parser_task.parse,
            "delay",
            lambda df_id, **kwargs: calls.append(("python", df_id)),
        )

        token = ParsingService.schedule(data_file_id=datafile.id)
        assert token is not None
        assert ("python", datafile.id) in calls

    def test_resolve_or_reuse_parser_mode(self, data_analyst):
        """Verify ParsingService.resolve_or_reuse_parser_mode persists and reuses mode."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=16)
        assert datafile.parser_mode is None

        mode1 = ParsingService.resolve_or_reuse_parser_mode(datafile.id)
        datafile.refresh_from_db()
        assert datafile.parser_mode == mode1

        # Second resolution returns persisted mode
        mode2 = ParsingService.resolve_or_reuse_parser_mode(datafile.id)
        assert mode2 == mode1


@pytest.mark.django_db
class TestParsingServiceModelAndModeResolution:
    """Tests for model mappings, shadow resolution, and parser mode routing."""

    def test_shadow_record_model_lookup(self):
        """Verify _shadow_record_model returns matching shadow model."""
        assert _shadow_record_model(TANF_T1) == ShadowTANF_T1

    def test_shadow_record_model_unmapped_raises_lookup_error(self):
        """Verify _shadow_record_model raises LookupError for unknown tables."""

        class UnmappedModel:
            class _meta:
                db_table = "nonexistent_table_xyz"

        with pytest.raises(LookupError, match="No shadow model found for table"):
            _shadow_record_model(UnmappedModel)

    def test_parser_models_for_mode_invalid_raises_value_error(self):
        """Verify _parser_models_for_mode raises ValueError for invalid modes."""
        with pytest.raises(ValueError, match="Unsupported Go parser table mode"):
            _parser_models_for_mode("unsupported_mode")

    def test_uses_shadow_table_helper(self):
        """Verify _uses_shadow_table handles None safely."""
        assert _uses_shadow_table(None) is False

    def test_program_code_and_section_name_helpers(self):
        """Verify _program_code and _section_name projection helpers."""
        assert _program_code(None) is None
        assert _section_name(None) is None

        class ObjWithDirectAttrs:
            section = "Direct Section"
            program_type = "SSP"

        assert _section_name(ObjWithDirectAttrs()) == "Direct Section"
        assert _program_code(ObjWithDirectAttrs()) == "SSP"


@pytest.mark.django_db
class TestSummaryStatusAndAggregates:
    """Tests for DataFileSummary status rules, aggregates, and record calculations."""

    def test_get_summary_status_returns_non_pending_status_immediately(self):
        """If dfs.status is not PENDING, return existing status without error query."""
        dfs = type("DFS", (), {"status": DataFileSummary.Status.ACCEPTED})()
        assert _get_summary_status(dfs, None) == DataFileSummary.Status.ACCEPTED

    def test_get_summary_status_precheck_error_returns_rejected(self, data_analyst):
        """A PRE_CHECK error sets summary status to REJECTED."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=21)
        dfs = DataFileSummary.objects.create(
            datafile=datafile, status=DataFileSummary.Status.PENDING
        )
        ParserError.objects.create(
            file=datafile,
            error_type=ParserErrorCategoryChoices.PRE_CHECK,
            error_message="Fatal precheck failure",
        )
        assert _get_summary_status(dfs, datafile) == DataFileSummary.Status.REJECTED

    def test_get_summary_status_partially_accepted(self, data_analyst):
        """RECORD_PRE_CHECK or CASE_CONSISTENCY errors set status to PARTIALLY_ACCEPTED."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=22)
        dfs = DataFileSummary.objects.create(
            datafile=datafile, status=DataFileSummary.Status.PENDING
        )
        ParserError.objects.create(
            file=datafile,
            error_type=ParserErrorCategoryChoices.RECORD_PRE_CHECK,
            error_message="Record error",
        )
        assert (
            _get_summary_status(dfs, datafile)
            == DataFileSummary.Status.PARTIALLY_ACCEPTED
        )

    def test_get_summary_status_accepted_with_errors(self, data_analyst):
        """Non-precheck/non-consistency errors set status to ACCEPTED_WITH_ERRORS."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=23)
        dfs = DataFileSummary.objects.create(
            datafile=datafile, status=DataFileSummary.Status.PENDING
        )
        ParserError.objects.create(
            file=datafile,
            error_type=ParserErrorCategoryChoices.FIELD_VALUE,
            error_message="Field value error",
        )
        assert (
            _get_summary_status(dfs, datafile)
            == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
        )

    def test_get_summary_status_clean_returns_accepted(self, data_analyst):
        """Zero errors results in ACCEPTED status."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=24)
        dfs = DataFileSummary.objects.create(
            datafile=datafile, status=DataFileSummary.Status.PENDING
        )
        assert _get_summary_status(dfs, datafile) == DataFileSummary.Status.ACCEPTED

    def test_calculate_total_records_variations(self):
        """Verify _calculate_total_records handles case aggregates and fallbacks."""
        assert _calculate_total_records(None) == 0

        # With case_aggregates months dictionary
        dfs_with_months = type(
            "DFS",
            (),
            {
                "case_aggregates": {
                    "months": [
                        {"accepted_without_errors": 10, "accepted_with_errors": 5},
                        {"accepted_without_errors": 20, "accepted_with_errors": 0},
                    ]
                }
            },
        )()
        assert _calculate_total_records(dfs_with_months) == 35

        # Fallback to total_number_of_records_in_file
        dfs_fallback_file = type(
            "DFS",
            (),
            {
                "case_aggregates": None,
                "total_number_of_records_in_file": 42,
                "total_number_of_records_created": 0,
            },
        )()
        assert _calculate_total_records(dfs_fallback_file) == 42

        # Fallback to total_number_of_records_created
        dfs_fallback_created = type(
            "DFS",
            (),
            {
                "case_aggregates": {},
                "total_number_of_records_in_file": 0,
                "total_number_of_records_created": 99,
            },
        )()
        assert _calculate_total_records(dfs_fallback_created) == 99

    def test_update_dfs_fra_aggregates(self, monkeypatch, data_analyst):
        """Verify update_dfs routes to fra_total_errors for FRA files."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=25,
            section=Section.objects.filter(
                name=Section.Name.FRA_WORK_OUTCOMES
            ).first(),
        )
        dfs = DataFileSummary.objects.create(
            datafile=datafile, status=DataFileSummary.Status.PENDING
        )
        fra_called = []
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service,
            "fra_total_errors",
            lambda *a, **k: fra_called.append(True) or {"fra": 1},
        )
        update_dfs(dfs, datafile)
        assert len(fra_called) == 1
        assert dfs.case_aggregates == {"fra": 1}

    def test_update_dfs_non_case_data_aggregates(self, monkeypatch, data_analyst):
        """Verify update_dfs routes to total_errors_by_month for non Case Data sections."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=26,
            section=Section.objects.filter(
                name=Section.Name.AGGREGATE_DATA
            ).first(),
        )
        dfs = DataFileSummary.objects.create(
            datafile=datafile, status=DataFileSummary.Status.PENDING
        )
        agg_called = []
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service,
            "total_errors_by_month",
            lambda *a, **k: agg_called.append(True) or {"agg": 1},
        )
        update_dfs(dfs, datafile)
        assert len(agg_called) == 1
        assert dfs.case_aggregates == {"agg": 1}


@pytest.mark.django_db
class TestReparseFlowAndNotifications:
    """Tests for reparse notifications and reparse metadata closure."""

    def test_should_send_reparse_notification_suppression_matrix(self):
        """Verify email notification suppression rules for reparse events."""
        # Non-reparse always sends email
        assert should_send_reparse_notification(None, None, reparse_id=None) is True

        # Missing file_meta sends email
        dfs = type("DFS", (), {"status": DataFileSummary.Status.ACCEPTED})()
        assert should_send_reparse_notification(dfs, None, reparse_id=1) is True

        # ACCEPTED -> ACCEPTED suppresses email
        file_meta_acc = type(
            "FileMeta",
            (),
            {"previous_summary_status": DataFileSummary.Status.ACCEPTED},
        )()
        dfs_acc = type("DFS", (), {"status": DataFileSummary.Status.ACCEPTED})()
        assert (
            should_send_reparse_notification(dfs_acc, file_meta_acc, reparse_id=1)
            is False
        )

        # REJECTED -> ACCEPTED sends email
        file_meta_rej = type(
            "FileMeta",
            (),
            {"previous_summary_status": DataFileSummary.Status.REJECTED},
        )()
        assert (
            should_send_reparse_notification(dfs_acc, file_meta_rej, reparse_id=1)
            is True
        )

        # ACCEPTED -> REJECTED sends email
        dfs_rej = type("DFS", (), {"status": DataFileSummary.Status.REJECTED})()
        assert (
            should_send_reparse_notification(dfs_rej, file_meta_acc, reparse_id=1)
            is True
        )

    def test_finalize_reparse_invokes_reparse_meta_totals(
        self, monkeypatch, data_analyst
    ):
        """Verify _finalize_reparse invokes ReparseMeta.set_total_num_records_post when finalized."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=27)
        dfs = DataFileSummary.objects.create(
            datafile=datafile,
            status=DataFileSummary.Status.ACCEPTED,
            total_number_of_records_created=50,
        )
        reparse_meta = ReparseMeta.objects.create(
            db_backup_location="s3://backup"
        )
        file_meta = ReparseFileMeta.objects.create(
            data_file=datafile,
            reparse_meta=reparse_meta,
            previous_summary_status=DataFileSummary.Status.ACCEPTED,
        )

        from tdpservice.parsers import service

        totals_called = []
        monkeypatch.setattr(service, "finish_reparse", lambda *a, **k: True)
        monkeypatch.setattr(
            ReparseMeta,
            "set_total_num_records_post",
            lambda meta: totals_called.append(meta.id),
        )

        _finalize_reparse(
            data_file=datafile,
            reparse_id=reparse_meta.id,
            file_meta=file_meta,
            dfs=dfs,
            reparse_success=True,
        )

        assert reparse_meta.id in totals_called


@pytest.mark.django_db
class TestShadowPostParseAndEngineFallback:
    """Tests for shadow table post-parsing and legacy engine fallbacks."""

    def test_post_parse_shadow_success(self, data_analyst):
        """Verify post_parse on a ShadowDataFile marks summary ACCEPTED and records transition."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=28,
            state=SubmissionState.VIRUS_SCAN_COMPLETED,
        )
        shadow_datafile = create_or_update_shadow_data_file(datafile)

        ps = ParsingService(data_file=shadow_datafile)
        ps.post_parse(table_mode="go-shadow")

        shadow_datafile.refresh_from_db()
        dfs = ShadowDataFileSummary.objects.get(datafile=shadow_datafile)
        assert dfs.status == DataFileSummary.Status.ACCEPTED
        assert shadow_datafile.state == SubmissionState.PARSE_COMPLETED

        transitions = DataFileStateTransition.objects.for_object(shadow_datafile)
        assert transitions.first().metadata.get("parser_class") == "GoParser"

    def test_post_parse_shadow_parse_error(self, data_analyst):
        """Verify post_parse on a ShadowDataFile handles parse_error."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=29,
            state=SubmissionState.VIRUS_SCAN_COMPLETED,
        )
        shadow_datafile = create_or_update_shadow_data_file(datafile)

        ps = ParsingService(data_file=shadow_datafile)
        ps.post_parse(parse_error="Shadow worker panic", table_mode="go-shadow")

        shadow_datafile.refresh_from_db()
        dfs = ShadowDataFileSummary.objects.get(datafile=shadow_datafile)
        assert dfs.status == DataFileSummary.Status.REJECTED
        assert shadow_datafile.state == SubmissionState.PARSE_FAILED

    def test_post_parse_shadow_idempotent_when_already_failed(self, data_analyst):
        """Verify post_parse on an already failed ShadowDataFile returns early."""
        datafile = DataFileFactory(
            stt=data_analyst.stt,
            version=30,
            state=SubmissionState.PARSE_FAILED,
        )
        shadow_datafile = create_or_update_shadow_data_file(datafile)
        initial_transitions = DataFileStateTransition.objects.for_object(
            shadow_datafile
        ).count()

        ps = ParsingService(data_file=shadow_datafile)
        ps.post_parse(parse_error="Duplicate error signal", table_mode="go-shadow")

        # No new transitions recorded
        assert (
            DataFileStateTransition.objects.for_object(shadow_datafile).count()
            == initial_transitions
        )

    def test_python_parser_engine_legacy_parse_method(self, monkeypatch, data_analyst):
        """Verify PythonParserEngine calls .parse() if .parse_and_validate() is absent."""
        datafile = DataFileFactory(stt=data_analyst.stt, version=31)

        class LegacyParserOnly:
            def __init__(self):
                self.parse_called = False

            def parse(self):
                self.parse_called = True

        legacy_parser = LegacyParserOnly()
        from tdpservice.parsers import service

        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: legacy_parser
        )

        engine = PythonParserEngine(data_file=datafile)
        result = engine.execute()
        assert result is legacy_parser
        assert legacy_parser.parse_called is True
