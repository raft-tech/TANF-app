"""Tests for async AV scanning tasks."""

from unittest.mock import Mock

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.tasks import (
    complete_av_scan_for_datafile,
    scan_datafile_for_virus,
)
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.security.models import ClamAVFileScan


@pytest.mark.django_db
class TestCompleteAvScanForDatafile:
    """Test complete_av_scan_for_datafile task."""

    def test_clean_scan_transitions_to_virus_scan_completed_and_queues_parse(self, mocker):
        """Test that a CLEAN scan result transitions to VIRUS_SCAN_COMPLETED and queues parsing."""
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
        mock_parse = mocker.patch("tdpservice.data_files.tasks.parser_task.parse.delay")

        complete_av_scan_for_datafile(data_file.id, scan_result="clean", note="Test scan")

        data_file.refresh_from_db()
        assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
        mock_parse.assert_called_once_with(data_file.id)

    def test_infected_scan_transitions_to_virus_scan_failed_no_parse(self, mocker):
        """Test that an INFECTED scan result transitions to VIRUS_SCAN_FAILED."""
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
        mock_parse = mocker.patch("tdpservice.data_files.tasks.parser_task.parse.delay")

        complete_av_scan_for_datafile(
            data_file.id, scan_result="infected", note="Test scan"
        )

        data_file.refresh_from_db()
        assert data_file.state == SubmissionState.VIRUS_SCAN_FAILED
        mock_parse.assert_not_called()

    def test_error_scan_transitions_to_virus_scan_failed_no_parse(self, mocker):
        """Test that an ERROR scan result transitions to VIRUS_SCAN_FAILED."""
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
        mock_parse = mocker.patch("tdpservice.data_files.tasks.parser_task.parse.delay")

        complete_av_scan_for_datafile(
            data_file.id, scan_result="error", note="ClamAV unavailable"
        )

        data_file.refresh_from_db()
        assert data_file.state == SubmissionState.VIRUS_SCAN_FAILED
        mock_parse.assert_not_called()

    def test_handles_missing_datafile_gracefully(self, mocker, caplog):
        """Test that task handles missing DataFile gracefully."""
        mock_parse = mocker.patch("tdpservice.data_files.tasks.parser_task.parse.delay")

        complete_av_scan_for_datafile(99999, scan_result="clean")

        assert "DataFile with id 99999 not found" in caplog.text
        mock_parse.assert_not_called()

    def test_duplicate_clean_scan_does_not_queue_parse_again(self, mocker):
        """Test that duplicate clean scan results do not queue parse multiple times."""
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_COMPLETED)
        mock_parse = mocker.patch("tdpservice.data_files.tasks.parser_task.parse.delay")

        complete_av_scan_for_datafile(data_file.id, scan_result="clean")

        data_file.refresh_from_db()
        assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
        mock_parse.assert_not_called()

    def test_failed_scan_deletes_file_from_storage(self, mocker):
        """Test that failed scan results trigger file deletion from storage."""
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
        mock_file_delete = mocker.patch("django.db.models.fields.files.FieldFile.delete")
        mock_parse = mocker.patch("tdpservice.data_files.tasks.parser_task.parse.delay")

        complete_av_scan_for_datafile(data_file.id, scan_result="infected")

        data_file.refresh_from_db()
        assert data_file.state == SubmissionState.VIRUS_SCAN_FAILED
        assert mock_file_delete.call_count == 1
        assert mock_file_delete.call_args.kwargs == {"save": True}
        mock_parse.assert_not_called()


@pytest.mark.django_db
class TestScanDatafileForVirus:
    """Test scan_datafile_for_virus task."""

    def test_clamav_disabled_queues_clean_result(self, mocker, settings):
        """Test that when ClamAV is disabled, scan is skipped and clean result is queued."""
        settings.CLAMAV_NEEDED = False
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)
        mock_complete = mocker.patch(
            "tdpservice.data_files.tasks.complete_av_scan_for_datafile.delay"
        )

        scan_datafile_for_virus(data_file.id)

        mock_complete.assert_called_once_with(
            data_file.id,
            scan_result="clean",
            note="Skipped AV scan (CLAMAV_NEEDED=False)",
        )

    def test_clean_scan_queues_completion_task(self, mocker, settings):
        """Test that a clean scan result queues the completion task."""
        settings.CLAMAV_NEEDED = True
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)

        mock_client = Mock()
        mock_client.scan_file.return_value = True
        mocker.patch("tdpservice.data_files.tasks.ClamAVClient", return_value=mock_client)

        mock_scan = Mock()
        mock_scan.result = ClamAVFileScan.Result.CLEAN
        mocker.patch(
            "tdpservice.data_files.tasks.ClamAVFileScan.objects.filter",
            return_value=Mock(
                order_by=Mock(return_value=Mock(first=Mock(return_value=mock_scan)))
            ),
        )

        mock_complete = mocker.patch(
            "tdpservice.data_files.tasks.complete_av_scan_for_datafile.delay"
        )

        scan_datafile_for_virus(data_file.id)

        mock_complete.assert_called_once()
        call_args = mock_complete.call_args
        assert call_args[0][0] == data_file.id
        assert call_args[1]["scan_result"] == "clean"

    def test_infected_scan_queues_completion_task(self, mocker, settings):
        """Test that an infected scan result queues the completion task."""
        settings.CLAMAV_NEEDED = True
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)

        mock_client = Mock()
        mock_client.scan_file.return_value = False
        mocker.patch("tdpservice.data_files.tasks.ClamAVClient", return_value=mock_client)

        mock_scan = Mock()
        mock_scan.result = ClamAVFileScan.Result.INFECTED
        mocker.patch(
            "tdpservice.data_files.tasks.ClamAVFileScan.objects.filter",
            return_value=Mock(
                order_by=Mock(return_value=Mock(first=Mock(return_value=mock_scan)))
            ),
        )

        mock_complete = mocker.patch(
            "tdpservice.data_files.tasks.complete_av_scan_for_datafile.delay"
        )

        scan_datafile_for_virus(data_file.id)

        mock_complete.assert_called_once()
        call_args = mock_complete.call_args
        assert call_args[0][0] == data_file.id
        assert call_args[1]["scan_result"] == "infected"

    def test_service_unavailable_queues_error_result(self, mocker, settings):
        """Test that ClamAV service unavailable queues error result."""
        settings.CLAMAV_NEEDED = True
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)

        from tdpservice.security.clients import ClamAVClient

        mock_client = Mock()
        mock_client.scan_file.side_effect = ClamAVClient.ServiceUnavailable()
        mocker.patch("tdpservice.data_files.tasks.ClamAVClient", return_value=mock_client)

        mock_complete = mocker.patch(
            "tdpservice.data_files.tasks.complete_av_scan_for_datafile.delay"
        )

        scan_datafile_for_virus(data_file.id)

        mock_complete.assert_called_once_with(
            data_file.id,
            scan_result="error",
            note="AV scan failed: ClamAV service unavailable",
        )

    def test_unexpected_error_queues_error_result(self, mocker, settings):
        """Test that unexpected errors queue error result."""
        settings.CLAMAV_NEEDED = True
        data_file = DataFileFactory(state=SubmissionState.VIRUS_SCAN_STARTED)

        mock_client = Mock()
        mock_client.scan_file.side_effect = Exception("Unexpected error")
        mocker.patch("tdpservice.data_files.tasks.ClamAVClient", return_value=mock_client)

        mock_complete = mocker.patch(
            "tdpservice.data_files.tasks.complete_av_scan_for_datafile.delay"
        )

        scan_datafile_for_virus(data_file.id)

        mock_complete.assert_called_once()
        call_args = mock_complete.call_args
        assert call_args[0][0] == data_file.id
        assert call_args[1]["scan_result"] == "error"
        assert "Unexpected error" in call_args[1]["note"]

    def test_handles_missing_datafile_gracefully(self, caplog):
        """Test that task handles missing DataFile gracefully."""
        scan_datafile_for_virus(99999)

        assert "DataFile with id 99999 not found" in caplog.text
