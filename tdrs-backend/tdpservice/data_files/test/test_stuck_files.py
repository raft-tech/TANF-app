import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import DataFileSummary
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.data_files.management.commands.find_pending_submissions import get_stuck_files


def _time_ago(hours=0, minutes=0, seconds=0):
    return datetime.now(tz=timezone.utc) - timedelta(hours=hours, minutes=minutes, seconds=seconds)


@pytest.mark.django_db
def test_find_pending_submissions__none_stuck(stt_user, stt):
    """Finds no stuck files."""
    df1 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df1.created_at = _time_ago(hours=2)
    df1.save()

    dfs1 = DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.ACCEPTED,
    )

    df2 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q2, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df2.created_at = _time_ago(hours=1)
    df2.save()

    dfs2 = DataFileSummary.objects.create(
        datafile=df2,
        status=DataFileSummary.Status.ACCEPTED,
    )

    rpm = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=1),
        finished=True,
        success=True,
        num_files_to_reparse=1,
        files_completed=1,
        files_failed=0,
    )

    df2.reparse_meta_models.add(rpm)

    df3 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q3, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df3.created_at = _time_ago(minutes=40)
    df3.save()

    dfs3 = DataFileSummary.objects.create(
        datafile=df3,
        status=DataFileSummary.Status.PENDING,
    )

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 0


@pytest.mark.django_db
def test_find_pending_submissions__non_reparse_stuck(stt_user, stt):
    """Finds standard upload/submission stuck in Pending."""
    df1 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df1.created_at = _time_ago(hours=2)
    df1.save()

    dfs1 = DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.PENDING,
    )

    df2 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q2, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df2.created_at = _time_ago(hours=1)
    df2.save()

    dfs2 = DataFileSummary.objects.create(
        datafile=df2,
        status=DataFileSummary.Status.ACCEPTED,
    )

    rpm = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=1),
        finished=True,
        success=True,
        num_files_to_reparse=1,
        files_completed=1,
        files_failed=0,
    )

    df2.reparse_meta_models.add(rpm)

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df1.pk


@pytest.mark.django_db
def test_find_pending_submissions__non_reparse_stuck__no_dfs(stt_user, stt):
    """Finds standard upload/submission stuck in Pending."""
    df1 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df1.created_at = _time_ago(hours=2)
    df1.save()

    df2 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q2, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df2.created_at = _time_ago(hours=1)
    df2.save()

    dfs2 = DataFileSummary.objects.create(
        datafile=df2,
        status=DataFileSummary.Status.ACCEPTED,
    )

    rpm = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=1),
        finished=True,
        success=True,
        num_files_to_reparse=1,
        files_completed=1,
        files_failed=0,
    )

    df2.reparse_meta_models.add(rpm)

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df1.pk


@pytest.mark.django_db
def test_find_pending_submissions__reparse_stuck(stt_user, stt):
    """Finds a reparse submission stuck in pending, past the timeout."""
    df1 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df1.created_at = _time_ago(hours=2)
    df1.save()

    dfs1 = DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.ACCEPTED,
    )

    df2 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q2, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df2.created_at = _time_ago(hours=1)
    df2.save()

    dfs2 = DataFileSummary.objects.create(
        datafile=df2,
        status=DataFileSummary.Status.PENDING,
    )

    rpm = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=1),
        finished=False,
        success=False,
        num_files_to_reparse=1,
        files_completed=0,
        files_failed=0,
    )

    df2.reparse_meta_models.add(rpm)

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df2.pk


@pytest.mark.django_db
def test_find_pending_submissions__reparse_stuck__no_dfs(stt_user, stt):
    """Finds a reparse submission stuck in pending, past the timeout."""
    df1 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df1.created_at = _time_ago(hours=2)
    df1.save()

    dfs1 = DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.ACCEPTED,
    )

    df2 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q2, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df2.created_at = _time_ago(hours=1)
    df2.save()

    rpm = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=1),
        finished=False,
        success=False,
        num_files_to_reparse=1,
        files_completed=0,
        files_failed=0,
    )

    df2.reparse_meta_models.add(rpm)

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df2.pk


@pytest.mark.django_db
def test_find_pending_submissions__reparse_and_non_reparse_stuck(stt_user, stt):
    """Finds stuck submissions, both reparse and standard parse."""
    df1 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df1.created_at = _time_ago(hours=2)
    df1.save()

    dfs1 = DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.PENDING,
    )

    df2 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q2, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df2.created_at = _time_ago(hours=1)
    df2.save()

    dfs2 = DataFileSummary.objects.create(
        datafile=df2,
        status=DataFileSummary.Status.PENDING,
    )

    rpm = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=1),
        finished=False,
        success=False,
        num_files_to_reparse=1,
        files_completed=0,
        files_failed=0,
    )

    df2.reparse_meta_models.add(rpm)

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 2
    for f in stuck_files:
        assert f.pk in (df1.pk, df2.pk)


@pytest.mark.django_db
def test_find_pending_submissions__reparse_and_non_reparse_stuck_no_dfs(stt_user, stt):
    """Finds stuck submissions, both reparse and standard parse."""
    df1 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df1.created_at = _time_ago(hours=2)
    df1.save()

    df2 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q2, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df2.created_at = _time_ago(hours=1)
    df2.save()

    rpm = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=1),
        finished=False,
        success=False,
        num_files_to_reparse=1,
        files_completed=0,
        files_failed=0,
    )

    df2.reparse_meta_models.add(rpm)

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 2
    for f in stuck_files:
        assert f.pk in (df1.pk, df2.pk)


@pytest.mark.django_db
def test_find_pending_submissions__old_reparse_stuck__new_not_stuck(stt_user, stt):
    """Finds no stuck files, as the new parse is successful."""
    df1 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df1.created_at = _time_ago(hours=2)
    df1.save()

    dfs1 = DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.PENDING,
    )

    # reparse fails the first time
    rpm1 = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=2),
        finished=False,
        success=False,
        num_files_to_reparse=1,
        files_completed=0,
        files_failed=0,
    )
    df1.reparse_meta_models.add(rpm1)

    # reparse again, succeeds this time
    dfs1.delete()  # reparse deletes the original dfs and creates the new one
    dfs2 = DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.ACCEPTED,
    )

    rpm2 = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=1),
        finished=True,
        success=True,
        num_files_to_reparse=1,
        files_completed=1,
        files_failed=0,
    )
    df1.reparse_meta_models.add(rpm2)

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 0


@pytest.mark.django_db
def test_find_pending_submissions__new_reparse_stuck__old_not_stuck(stt_user, stt):
    """Finds files stuck from the new reparse, even though the old one was successful."""
    df1 = DataFile.objects.create(
        quarter=DataFile.Quarter.Q1, section=DataFile.Section.ACTIVE_CASE_DATA,
        year=2023, version=1, user=stt_user, stt=stt
    )
    df1.created_at = _time_ago(hours=2)
    df1.save()

    dfs1 = DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.REJECTED,
    )

    # reparse fails the first time
    rpm1 = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=2),
        finished=False,
        success=False,
        num_files_to_reparse=1,
        files_completed=0,
        files_failed=0,
    )
    df1.reparse_meta_models.add(rpm1)

    # reparse again, succeeds this time
    dfs1.delete()  # reparse deletes the original dfs and creates the new one
    dfs2 = DataFileSummary.objects.create(
        datafile=df1,
        status=DataFileSummary.Status.PENDING,
    )

    rpm2 = ReparseMeta.objects.create(
        timeout_at=_time_ago(hours=1),
        finished=True,
        success=True,
        num_files_to_reparse=1,
        files_completed=1,
        files_failed=0,
    )
    df1.reparse_meta_models.add(rpm2)

    stuck_files = get_stuck_files()
    assert stuck_files.count() == 1
    assert stuck_files.first().pk == df1.pk
