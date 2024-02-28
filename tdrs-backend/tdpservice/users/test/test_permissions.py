"""Test appropriate permissions are assigned to each Group."""
import pytest


@pytest.mark.django_db
def test_ofa_admin_permissions(ofa_admin):
    """Test that an OFA Admin user inherits the correct permissions."""
    expected_permissions = {
        'admin.view_logentry',
        'auth.view_group',
        'data_files.add_datafile',
        'data_files.view_datafile',
        'security.view_clamavfilescan',
        'security.view_owaspzapscan',
        'stts.view_region',
        'stts.view_stt',
        'users.add_user',
        'users.change_user',
        'users.view_user',
    }
    group_permissions = ofa_admin.get_group_permissions()
    assert group_permissions == expected_permissions


@pytest.mark.django_db
def test_ofa_system_admin_permissions(ofa_system_admin):
    """Test that an OFA System Admin user inherits the correct permissions."""
    expected_permissions = {
        'admin.add_logentry',
        'admin.change_logentry',
        'admin.view_logentry',
        'admin_interface.add_theme',
        'admin_interface.change_theme',
        'admin_interface.view_theme',
        'auth.add_group',
        'auth.add_permission',
        'auth.change_group',
        'auth.change_permission',
        'auth.view_group',
        'auth.view_permission',
        'authtoken.add_token',
        'authtoken.add_tokenproxy',
        'authtoken.change_token',
        'authtoken.change_tokenproxy',
        'authtoken.view_token',
        'authtoken.view_tokenproxy',
        'contenttypes.add_contenttype',
        'contenttypes.change_contenttype',
        'contenttypes.view_contenttype',
        'core.add_globalpermission',
        'core.change_globalpermission',
        'core.view_globalpermission',
        'data_files.add_datafile',
        'data_files.change_datafile',
        'data_files.view_datafile',
        'security.view_clamavfilescan',
        'security.view_owaspzapscan',
        'sessions.add_session',
        'sessions.change_session',
        'sessions.view_session',
        'stts.add_region',
        'stts.add_stt',
        'stts.change_region',
        'stts.change_stt',
        'stts.view_region',
        'stts.view_stt',
        'users.change_user',
        'users.view_user',
        'data_files.view_legacyfiletransfer',
        'data_files.add_legacyfiletransfer',
        'data_files.change_legacyfiletransfer',
        'django_celery_beat.add_clockedschedule',
        'django_celery_beat.add_crontabschedule',
        'django_celery_beat.add_intervalschedule',
        'django_celery_beat.add_periodictask',
        'django_celery_beat.add_periodictasks',
        'django_celery_beat.add_solarschedule',
        'django_celery_beat.change_clockedschedule',
        'django_celery_beat.change_crontabschedule',
        'django_celery_beat.change_intervalschedule',
        'django_celery_beat.change_periodictask',
        'django_celery_beat.change_periodictasks',
        'django_celery_beat.change_solarschedule',
        'django_celery_beat.view_clockedschedule',
        'django_celery_beat.view_crontabschedule',
        'django_celery_beat.view_intervalschedule',
        'django_celery_beat.view_periodictask',
        'django_celery_beat.view_periodictasks',
        'django_celery_beat.view_solarschedule',
        'search_indexes.add_tanf_t1',
        'search_indexes.view_tanf_t1',
        'search_indexes.change_tanf_t1',
        'search_indexes.add_tanf_t2',
        'search_indexes.view_tanf_t2',
        'search_indexes.change_tanf_t2',
        'search_indexes.add_tanf_t3',
        'search_indexes.view_tanf_t3',
        'search_indexes.change_tanf_t3',
        'search_indexes.add_tanf_t4',
        'search_indexes.view_tanf_t4',
        'search_indexes.change_tanf_t4',
        'search_indexes.add_tanf_t5',
        'search_indexes.view_tanf_t5',
        'search_indexes.change_tanf_t5',
        'search_indexes.add_tanf_t6',
        'search_indexes.view_tanf_t6',
        'search_indexes.change_tanf_t6',
        'search_indexes.add_tanf_t7',
        'search_indexes.view_tanf_t7',
        'search_indexes.change_tanf_t7',
        'parsers.add_parsererror',
        'parsers.change_parsererror',
        'parsers.view_parsererror',
        'parsers.add_datafilesummary',
        'parsers.view_datafilesummary',
        'parsers.change_datafilesummary',
        'search_indexes.add_ssp_m1',
        'search_indexes.view_ssp_m1',
        'search_indexes.change_ssp_m1',
        'search_indexes.add_ssp_m2',
        'search_indexes.view_ssp_m2',
        'search_indexes.change_ssp_m2',
        'search_indexes.add_ssp_m3',
        'search_indexes.view_ssp_m3',
        'search_indexes.change_ssp_m3',
        'search_indexes.add_ssp_m4',
        'search_indexes.view_ssp_m4',
        'search_indexes.change_ssp_m4',
        'search_indexes.add_ssp_m5',
        'search_indexes.view_ssp_m5',
        'search_indexes.change_ssp_m5',
        'search_indexes.add_ssp_m6',
        'search_indexes.view_ssp_m6',
        'search_indexes.change_ssp_m6',
        'search_indexes.add_ssp_m7',
        'search_indexes.view_ssp_m7',
        'search_indexes.change_ssp_m7',
        'search_indexes.add_tribal_tanf_t1',
        'search_indexes.view_tribal_tanf_t1',
        'search_indexes.change_tribal_tanf_t1',
        'search_indexes.add_tribal_tanf_t2',
        'search_indexes.view_tribal_tanf_t2',
        'search_indexes.change_tribal_tanf_t2',
        'search_indexes.add_tribal_tanf_t3',
        'search_indexes.view_tribal_tanf_t3',
        'search_indexes.change_tribal_tanf_t3',
        'search_indexes.add_tribal_tanf_t4',
        'search_indexes.view_tribal_tanf_t4',
        'search_indexes.change_tribal_tanf_t4',
        'search_indexes.add_tribal_tanf_t5',
        'search_indexes.view_tribal_tanf_t5',
        'search_indexes.change_tribal_tanf_t5',
        'search_indexes.add_tribal_tanf_t6',
        'search_indexes.view_tribal_tanf_t6',
        'search_indexes.change_tribal_tanf_t6',
        'search_indexes.add_tribal_tanf_t7',
        'search_indexes.view_tribal_tanf_t7',
        'search_indexes.change_tribal_tanf_t7',
    }
    group_permissions = ofa_system_admin.get_group_permissions()
    assert group_permissions == expected_permissions


@pytest.mark.django_db
def test_data_analyst_permissions(data_analyst):
    """Test that a Data Analyst user inherits the correct permissions."""
    expected_permissions = {
        'data_files.add_datafile',
        'data_files.view_datafile',
    }
    group_permissions = data_analyst.get_group_permissions()
    assert group_permissions == expected_permissions

@pytest.mark.django_db
def test_digit_team_permissions(digit_team):
    """Test that a DIGIT Team user inherits the correct permissions."""
    expected_permissions = {
        'data_files.view_datafile',
        'parsers.view_datafilesummary',
        'parsers.view_parsererror',
    }
    group_permissions = digit_team.get_group_permissions()
    assert group_permissions == expected_permissions
