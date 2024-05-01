"""Package level fixtures."""
import pytest
from tdpservice.parsers.test.factories import DataFileSummaryFactory, ParsingFileFactory
from tdpservice.parsers import util

@pytest.fixture
def test_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_correct_file.txt', stt_user, stt)

@pytest.fixture
def test_header_datafile(stt_user, stt):
    """Fixture for header test."""
    return util.create_test_datafile('tanf_section1_header_test.txt', stt_user, stt)

@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.build()

@pytest.fixture
def t2_invalid_dob_file():
    """Fixture for T2 file with an invalid DOB."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='t2_invalid_dob_file.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20204A25   TAN1ED\n'
                    b'T22020101111111111212Q897$9 3WTTTTTY@W222122222222101221211001472201140000000000000000000000000'
                    b'0000000000000000000000000000000000000000000000000000000000291\n'
                    b'TRAILER0000001         ')
    )
    return parsing_file

@pytest.fixture
def test_big_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP1.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP1.TS06', stt_user, stt)

@pytest.fixture
def bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S2."""
    return util.create_test_datafile('bad_TANF_S2.txt', stt_user, stt)

@pytest.fixture
def bad_file_missing_header(stt_user, stt):
    """Fixture for bad_missing_header."""
    return util.create_test_datafile('bad_missing_header.txt', stt_user, stt)

@pytest.fixture
def bad_file_multiple_headers(stt_user, stt):
    """Fixture for bad_two_headers."""
    return util.create_test_datafile('bad_two_headers.txt', stt_user, stt)

@pytest.fixture
def big_bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S1."""
    return util.create_test_datafile('bad_TANF_S1.txt', stt_user, stt)

@pytest.fixture
def bad_trailer_file(stt_user, stt):
    """Fixture for bad_trailer_1."""
    return util.create_test_datafile('bad_trailer_1.txt', stt_user, stt)

@pytest.fixture
def bad_trailer_file_2(stt_user, stt):
    """Fixture for bad_trailer_2."""
    return util.create_test_datafile('bad_trailer_2.txt', stt_user, stt)

@pytest.fixture
def empty_file(stt_user, stt):
    """Fixture for empty_file."""
    return util.create_test_datafile('empty_file', stt_user, stt)

@pytest.fixture
def small_ssp_section1_datafile(stt_user, stt):
    """Fixture for small_ssp_section1."""
    return util.create_test_datafile('small_ssp_section1.txt', stt_user, stt, 'SSP Active Case Data')

@pytest.fixture
def ssp_section1_datafile(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return util.create_test_datafile('ssp_section1_datafile.txt', stt_user, stt, 'SSP Active Case Data')

@pytest.fixture
def small_tanf_section1_datafile(stt_user, stt):
    """Fixture for small_tanf_section1."""
    return util.create_test_datafile('small_tanf_section1.txt', stt_user, stt)

@pytest.fixture
def super_big_s1_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM1.TS53_fake."""
    return util.create_test_datafile('ADS.E2J.NDM1.TS53_fake.txt', stt_user, stt)

@pytest.fixture
def big_s1_rollback_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM1.TS53_fake.rollback."""
    return util.create_test_datafile('ADS.E2J.NDM1.TS53_fake.rollback.txt', stt_user, stt)

@pytest.fixture
def bad_tanf_s1__row_missing_required_field(stt_user, stt):
    """Fixture for small_tanf_section1."""
    return util.create_test_datafile('small_bad_tanf_s1.txt', stt_user, stt)

@pytest.fixture
def bad_ssp_s1__row_missing_required_field(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return util.create_test_datafile('small_bad_ssp_s1.txt', stt_user, stt, 'SSP Active Case Data')

@pytest.fixture
def small_tanf_section2_file(stt_user, stt):
    """Fixture for tanf section2 datafile."""
    return util.create_test_datafile('small_tanf_section2.txt', stt_user, stt, 'Closed Case Data')

@pytest.fixture
def tanf_section2_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP2.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP2.TS06', stt_user, stt, 'Closed Case Data')

@pytest.fixture
def tanf_section3_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP3.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP3.TS06', stt_user, stt, "Aggregate Data")

@pytest.fixture
def tanf_section1_file_with_blanks(stt_user, stt):
    """Fixture for ADS.E2J.FTP3.TS06."""
    return util.create_test_datafile('tanf_section1_blanks.txt', stt_user, stt)

@pytest.fixture
def tanf_section4_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP4.TS06', stt_user, stt, "Stratum Data")

@pytest.fixture
def bad_tanf_section4_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('bad_tanf_section_4.txt', stt_user, stt, "Stratum Data")

@pytest.fixture
def ssp_section4_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM4.MS24."""
    return util.create_test_datafile('ADS.E2J.NDM4.MS24', stt_user, stt, "SSP Stratum Data")

@pytest.fixture
def ssp_section2_rec_oadsi_file(stt_user, stt):
    """Fixture for sp_section2_rec_oadsi_file."""
    return util.create_test_datafile('ssp_section2_rec_oadsi_file.txt', stt_user, stt, 'SSP Closed Case Data')

@pytest.fixture
def ssp_section2_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM2.MS24."""
    return util.create_test_datafile('ADS.E2J.NDM2.MS24', stt_user, stt, 'SSP Closed Case Data')

@pytest.fixture
def ssp_section3_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP3.TS06."""
    return util.create_test_datafile('ADS.E2J.NDM3.MS24', stt_user, stt, "SSP Aggregate Data")

@pytest.fixture
def tribal_section_1_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP1.TS142', stt_user, stt, "Tribal Active Case Data")

@pytest.fixture
def tribal_section_1_inconsistency_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('tribal_section_1_inconsistency.txt', stt_user, stt, "Tribal Active Case Data")

@pytest.fixture
def tribal_section_2_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP2.TS142.txt', stt_user, stt, "Tribal Closed Case Data")

@pytest.fixture
def tribal_section_3_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP3.TS142."""
    return util.create_test_datafile('ADS.E2J.FTP3.TS142', stt_user, stt, "Tribal Aggregate Data")

@pytest.fixture
def tribal_section_4_file(stt_user, stt):
    """Fixture for tribal_section_4_fake.txt."""
    return util.create_test_datafile('tribal_section_4_fake.txt', stt_user, stt, "Tribal Stratum Data")

@pytest.fixture
def tanf_section_4_file_with_errors(stt_user, stt):
    """Fixture for tanf_section4_with_errors."""
    return util.create_test_datafile('tanf_section4_with_errors.txt', stt_user, stt, "Stratum Data")

@pytest.fixture
def no_records_file(stt_user, stt):
    """Fixture for tanf_section4_with_errors."""
    return util.create_test_datafile('no_records.txt', stt_user, stt)

@pytest.fixture
def tanf_section_1_file_with_bad_update_indicator(stt_user, stt):
    """Fixture for tanf_section_1_file_with_bad_update_indicator."""
    return util.create_test_datafile('tanf_s1_bad_update_indicator.txt', stt_user, stt, "Active Case Data")

@pytest.fixture
def tribal_section_4_bad_quarter(stt_user, stt):
    """Fixture for tribal_section_4_bad_quarter."""
    return util.create_test_datafile('tribal_section_4_fake_bad_quarter.txt', stt_user, stt, "Tribal Stratum Data")

@pytest.fixture
def tanf_s1_exact_dup_file():
    """Fixture for a section 1 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='s1_exact_duplicate.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20204A06   TAN1 D\n'
                    b'T12020101111111111223003403361110212120000300000000000008730010000000000000000000000' +
                    b'000000000000222222000000002229012                                       \n'
                    b'T12020101111111111223003403361110212120000300000000000008730010000000000000000000000' +
                    b'000000000000222222000000002229012                                       \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s2_exact_dup_file():
    """Fixture for a section 2 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        section="Closed Case Data",
        file__name='s2_exact_duplicate.txt',
        file__section='Closed Case Data',
        file__data=(b'HEADER20204C06   TAN1ED\n'
                    b'T42020101111111115825301400141123113                                   \n'
                    b'T42020101111111115825301400141123113                                   \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s3_exact_dup_file():
    """Fixture for a section 3 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2022,
        quarter='Q1',
        section="Aggregate Data",
        file__name='s3_exact_duplicate.txt',
        file__section='Aggregate Data',
        file__data=(b'HEADER20214G06   TAN1 D\n'
                    b'T620214000127470001104500011146000043010000397700003924000084460000706800007222'
                    b'0000550428490000551413780000566432530007558100075921000755420000098100000970000'
                    b'0096800039298000393490003897200035302000356020003560200168447001690470016810700'
                    b'0464480004649800046203001219990012254900121904000001630000014900000151000003440'
                    b'000033100000276000002580000024100000187000054530000388100003884\n'
                    b'T620214000127470001104500011146000043010000397700003924000084460000706800007222'
                    b'0000550428490000551413780000566432530007558100075921000755420000098100000970000'
                    b'0096800039298000393490003897200035302000356020003560200168447001690470016810700'
                    b'0464480004649800046203001219990012254900121904000001630000014900000151000003440'
                    b'000033100000276000002580000024100000187000054530000388100003884\n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s4_exact_dup_file():
    """Fixture for a section 4 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2022,
        quarter='Q1',
        section="Stratum Data",
        file__name='s4_exact_duplicate.txt',
        file__section='Stratum Data',
        file__data=(b'HEADER20214S06   TAN1 D\n'
                    b'T720214101006853700680540068454103000312400037850003180104000347400036460003583106'
                    b'000044600004360000325299000506200036070003385202000039100002740000499             '
                    b'                                                                                   \n'
                    b'T720214101006853700680540068454103000312400037850003180104000347400036460003583106'
                    b'000044600004360000325299000506200036070003385202000039100002740000499             '
                    b'                                                                                   \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s1_exact_dup_file():
    """Fixture for a section 1 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2019,
        quarter='Q1',
        section='SSP Active Case Data',
        file__name='s1_exact_duplicate.txt',
        file__section='SSP Active Case Data',
        file__data=(b'HEADER20184A24   SSP1ED\n'
                    b'M12018101111111112721401400351021331100273000000000000000105400000000000000000000000000000'
                    b'00000222222000000002229                                     \n'
                    b'M12018101111111112721401400351021331100273000000000000000105400000000000000000000000000000'
                    b'00000222222000000002229                                     \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s2_exact_dup_file():
    """Fixture for a section 2 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2019,
        quarter='Q1',
        section="SSP Closed Case Data",
        file__name='s2_exact_duplicate.txt',
        file__section='SSP Closed Case Data',
        file__data=(b'HEADER20184C24   SSP1ED\n'
                    b'M42018101111111116120000406911161113                              \n'
                    b'M42018101111111116120000406911161113                              \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s3_exact_dup_file():
    """Fixture for a section 3 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2022,
        quarter='Q1',
        section="SSP Aggregate Data",
        file__name='s3_exact_duplicate.txt',
        file__section='SSP Aggregate Data',
        file__data=(b'HEADER20214G24   SSP1 D\n'
                    b'M6202140001586900016008000159560000086100000851000008450001490500015055000150130000010300000'
                    b'10200000098000513550005169600051348000157070001581400015766000356480003588200035582000000000'
                    b'000000000000000000000000000000000000000000000000000000012020000118900001229\n'
                    b'M6202140001586900016008000159560000086100000851000008450001490500015055000150130000010300000'
                    b'10200000098000513550005169600051348000157070001581400015766000356480003588200035582000000000'
                    b'000000000000000000000000000000000000000000000000000000012020000118900001229\n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s4_exact_dup_file():
    """Fixture for a section 4 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2022,
        quarter='Q1',
        section="SSP Stratum Data",
        file__name='s4_exact_duplicate.txt',
        file__section='SSP Stratum Data',
        file__data=(b'HEADER20214S24   SSP1 D\n'
                    b'M7202141010001769000131000011111020000748000076700007681030013352001393100140772000001202000'
                    b'11890001229                                                                                 '
                    b'                                                               \n'
                    b'M7202141010001769000131000011111020000748000076700007681030013352001393100140772000001202000'
                    b'11890001229                                                                                 '
                    b'                                                               \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s1_partial_dup_file():
    """Fixture for a section 1 file containing an partial duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='s1_partial_duplicate.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20204A06   TAN1 D\n'
                    b'T120201011111111112230034033611102121200003000000000000087300100000000000000' +
                    b'00000000000000000000222222000000002229012                                       \n'
                    b'T1202010111111111122300340336111021212000030000000000000873001000000000000000' +
                    b'0000000000000000000222222000000002229013                                       \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s2_partial_dup_file():
    """Fixture for a section 2 file containing an partial duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        section="Closed Case Data",
        file__name='s2_partial_duplicate.txt',
        file__section='Closed Case Data',
        file__data=(b'HEADER20204C06   TAN1ED\n'
                    b'T42020101111111115825301400141123113                                   \n'
                    b'T42020101111111115825301400141123114                                   \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s1_partial_dup_file():
    """Fixture for a section 1 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2019,
        quarter='Q1',
        section='SSP Active Case Data',
        file__name='s1_exact_duplicate.txt',
        file__section='SSP Active Case Data',
        file__data=(b'HEADER20184A24   SSP1ED\n'
                    b'M12018101111111112721401400351021331100273000000000000000105400000000000000000000000000'
                    b'00000000222222000000002229                                     \n'
                    b'M12018101111111112721401400351021331100273000000000000000105400000000000000000000000000'
                    b'00000000222222000000002228                                     \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s2_partial_dup_file():
    """Fixture for a section 2 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2019,
        quarter='Q1',
        section="SSP Closed Case Data",
        file__name='s2_exact_duplicate.txt',
        file__section='SSP Closed Case Data',
        file__data=(b'HEADER20184C24   SSP1ED\n'
                    b'M42018101111111116120000406911161113                              \n'
                    b'M42018101111111116120000406911161112                              \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file
