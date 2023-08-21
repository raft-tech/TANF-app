"""Tests and ensures cat 4 validation is working as expected."""

import pytest
from ..models import ParserError, ParserErrorCategoryChoices, DataFileSummary
from ..schema_defs import header, trailer
from ..schema_defs.tanf import active_section
from tdpservice.parsers import util
from .factories import DataFileSummaryFactory
from tdpservice.data_files.models import DataFile

@pytest.fixture
def test_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_correct_file', stt_user, stt)

@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.create()

class TestCat4Validation:
    """Tests cat4 validation."""

    @pytest.mark.django_db
    def test_cat4_header(self, test_datafile, dfs):
        """Test pen for class 4 validation."""
        x = util.get_text_from_df(test_datafile)
        x_prog = x['program_type']
        x_section = x['section']
        
        models = list((util.get_program_models(x_prog, x_section)).values())
        models.append(header)

        active_section_schema_manager = active_section.SectionSchemaManager(
            schema_managers=models
        )

        #TODO: create header object/model from test_datafile
        raw_header = test_datafile.file.readline()
        line=raw_header.decode().strip('\r\n')
        header_obj = header.parse_and_validate(
            line,
            util.make_generate_parser_error(test_datafile, 1)
        )
        print(header_obj)
        record, is_valid, errors = header_obj[0]

        active_section_schema_manager.parse_and_validate(test_datafile, util.make_generate_parser_error)

        # TODO: header date vs RMY checks
    
    @pytest.mark.django_db
    def test_cat4_tanf_active(self, test_datafile, dfs):
        """Run essential checks for TANF/A."""
        # active cases
        # TODO: t2 should have matching t1 via case_number and RMY

        # TODO: t3 should have matching t1 via case_number and RMY

        # TODO: t1 should have matching t2/t3 via case_number, RMY if fam_affil==1
        pass

    # closed cases
    # same header checks

    """
    HE, T5	
        if item 1 == 66, 72, or 78 and (calculated) AGE >= 19, 
        then item 19C == 1 or 2	adults in territories must have a valid value for 19C;

         requires calculating AGE: DOB (item #15) must be valid; 
         convert RPT_MON_YEAR (item #4) to YYYYMMDD and set DD to 01; 
         AGE formula: (rpt_month_year - DOB)/365.25
    """
    # test for above

    """
    HE, T5	
        if item 1 == 01-02,04-06,08-13,15-42,44-51,53-56 
        then item 19C != 1	people in states shouldn’t have value of 1
    """
    # test for above
    

    """
    HE, T5	
        if item 1 == 01-02,04-06,08-13,15-42,44-51,53-56, 
        then item 19E == 1 or 2	people in states must have valid value
    """
    # test for above
    

    """
    T4, T5	
        if (T4) item 9 == 01, 
        then at least one corresponding T5 record with the same RPT_MONTH_YEAR and CASE_NUMBER 
        should have item 28 == 1	
        if case closure reason = 01:employment,
             then at least one person on the case must have employment status = 1:Yes in the same month
    """
    # test for above
    

    """
    T4, T5	
        if (T4) item 9 == 03, 
        then at least one corresponding T5 record with the same RPT_MONTH_YEAR and CASE_NUMBER 
        should have item 21 == 01 or 02 and item 26 >= 060	
        if closure reason = FTL, 
            then at least one person who is HoH or spouse of HoH on case must have FTL months >=60 
    """
    # test for above
    

