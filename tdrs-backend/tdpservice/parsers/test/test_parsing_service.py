"""Unit tests for ParsingService and ParseResult."""

import io
import uuid

from django.db.utils import DatabaseError

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile, DataFileStateTransition
from tdpservice.data_files.submission_lifecycle import StaleParseOwnership
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.models import DataFileSummary, ParseExecutionLog, ParserError
from tdpservice.parsers.parser_classes.tdr_parser import TanfDataReportParser
from tdpservice.parsers.service import ParseResult, ParsingService
from tdpservice.parsers.util import DecoderUnknownException


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
    DataFile.Section.ACTIVE_CASE_DATA: "ADS.E2J.FTP1.TS72",
    DataFile.Section.CLOSED_CASE_DATA: "ADS.E2J.FTP2.TS72",
    DataFile.Section.AGGREGATE_DATA: "ADS.E2J.FTP3.TS72",
    DataFile.Section.STRATUM_DATA: "ADS.E2J.FTP4.TS72",
    DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS: "ADS.FRA.FTP1.TS72",
    DataFile.Section.FRA_SECONDRY_SCHOOL_ATTAINMENT: "ADS.FRA.FTP2.TS72",
    DataFile.Section.FRA_SUPPLEMENT_WORK_OUTCOMES: "ADS.FRA.FTP3.TS72",
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
class TestParsingServicePreconditions:
    """Tests for ParsingService data fetching and precondition checks."""

    def test_fetch_data_file_by_id(self, data_analyst):
        """Fetch DataFile instance by ID."""
        datafile = DataFileFactory(stt=data_analyst.stt)
        service = ParsingService(data_file_id=datafile.id)
        fetched = service.fetch_data_file()
        assert fetched.id == datafile.id

    def test_fetch_data_file_already_provided(self, data_analyst):
        """Use provided DataFile instance without DB lookup."""
        datafile = DataFileFactory(stt=data_analyst.stt)
        service = ParsingService(data_file=datafile)
        assert service.fetch_data_file() is datafile

    def test_fetch_data_file_missing_id_and_instance(self):
        """Raise ValueError when neither ID nor instance is provided."""
        service = ParsingService()
        with pytest.raises(ValueError, match="Neither data_file nor data_file_id was provided"):
            service.fetch_data_file()

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
            program_type=DataFile.ProgramType.TANF,
            section=DataFile.Section.ACTIVE_CASE_DATA,
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
        ps = ParsingService(data_file_id=datafile.id, event_id=event_id)
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

    def test_parse_decoder_unknown_returns_failed_result(self, monkeypatch, data_analyst):
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

        ps = ParsingService(data_file_id=datafile.id)
        result = ps.run()

        assert result.success is False
        assert "unknown encoding" in result.error_message
        datafile.refresh_from_db()
        assert datafile.state == SubmissionState.PARSE_FAILED

    def test_parse_database_error_returns_failed_result(self, monkeypatch, data_analyst):
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

        ps = ParsingService(data_file_id=datafile.id)
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

        ps = ParsingService(data_file_id=datafile.id)
        result = ps.run()

        assert result.success is False
        assert "unexpected parser crash" in result.error_message
        datafile.refresh_from_db()
        assert datafile.state == SubmissionState.PARSE_FAILED
        assert ParserError.objects.filter(file=datafile).exists()

    def test_parse_nonexistent_datafile_id_returns_failed_result(self):
        """Return failure ParseResult when DataFile id does not exist."""
        ps = ParsingService(data_file_id=99999999)
        result = ps.run()
        assert result.success is False
        assert result.data_file is None
        assert result.error_message is not None

    def test_parse_records_execution_log_on_success(self, monkeypatch, data_analyst):
        """Verify ParseExecutionLog is recorded on successful parse."""
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

        ps = ParsingService(data_file_id=datafile.id)
        result = ps.run()

        assert result.success is True
        logs = ParseExecutionLog.objects.for_object(datafile)
        assert logs.count() == 1
        log = logs.first()
        assert log.event_type == "parse_execution"
        assert log.status == DataFileSummary.Status.ACCEPTED
        assert log.parser_class == "DummyParser"
        assert log.execution_duration_ms is not None
        assert log.execution_duration_ms >= 0
        assert log.total_records_processed == 0
        assert log.total_errors_generated == 0
        assert log.metadata.get("success") is True

    def test_parse_records_execution_log_on_failure(self, monkeypatch, data_analyst):
        """Verify ParseExecutionLog is recorded on parse failure."""
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

        ps = ParsingService(data_file_id=datafile.id)
        result = ps.run()

        assert result.success is False
        logs = ParseExecutionLog.objects.for_object(datafile)
        assert logs.count() == 1
        log = logs.first()
        assert log.event_type == "parse_execution"
        assert "unexpected crash" in log.note
        assert log.execution_duration_ms is not None
        assert log.metadata.get("success") is False

    def test_parse_execution_log_error_does_not_break_run(self, monkeypatch, data_analyst):
        """Verify that an error while writing ParseExecutionLog does not affect ParseResult."""
        datafile = DataFileFactory(
            stt=data_analyst.stt, version=6, state=SubmissionState.VIRUS_SCAN_COMPLETED
        )
        ensure_stt_filenames(datafile.stt)
        setup_service_mocks(monkeypatch)

        dummy_parser = DummyParser()
        from tdpservice.parsers import service
        monkeypatch.setattr(
            service.ParserFactory, "get_instance", lambda **kwargs: dummy_parser
        )
        monkeypatch.setattr(service, "send_data_submitted_email", lambda *a, **k: None)

        def raise_db_error(*args, **kwargs):
            raise DatabaseError("DB disk full")

        monkeypatch.setattr(ParseExecutionLog.objects, "create_for_object", raise_db_error)

        ps = ParsingService(data_file_id=datafile.id)
        result = ps.run()

        # ParseResult should still succeed and not raise DatabaseError out
        assert result.success is True
