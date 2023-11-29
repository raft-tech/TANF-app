"""Tests and ensures cat 4 validation is working as expected."""

import pytest
from ..models import ParserError, ParserErrorCategoryChoices, DataFileSummary
from ..schema_defs import header, trailer
from ..schema_defs.tanf import active_section
from tdpservice.parsers import util, parse
from .factories import DataFileSummaryFactory
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.models import tanf

@pytest.fixture
def test_cat4_rmy(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_bad_tanf_s1_cat4_rmy', stt_user, stt)
                                     #small_correct_file', stt_user, stt)
@pytest.fixture
def test_cat4_tanfa(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_tanf_section1.txt', stt_user, stt)

@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.create()

class TestCat4Validation:
    """Tests cat4 validation."""

    @pytest.mark.django_db
    def test_cat4_header(self, test_cat4_rmy, dfs):
        """Test pen for class 4 validation."""
        x = util.get_text_from_df(test_cat4_rmy)
        x_prog = x['program_type']
        x_section = x['section']
        
        models = list((util.get_program_models(x_prog, x_section)).values())
        models.append(header)

        # active_section_schema_manager = active_section.SectionSchemaManager(
        #     schema_managers=models
        # )

        # #TODO: create header object/model from test_datafile
        # raw_header = test_datafile.file.readline()
        # line=raw_header.decode().strip('\r\n')
        # validate_results = header.parse_and_validate(
        #     line,
        #     util.make_generate_parser_error(test_datafile, 1)
        # )
        # print(validate_results)
        # record, is_valid, errors = validate_results[0]

        dfs.datafile = test_cat4_rmy
        dfs.save()

        errors = parse.parse_datafile(test_cat4_rmy)
        dfs.status = dfs.get_status()


        #active_section_schema_manager.parse_and_validate(test_datafile, util.make_generate_parser_error)

        # TODO: header date vs RMY checks
        year, header_rmy = util.fiscal_to_calendar(test_cat4_rmy.year, test_cat4_rmy.quarter)
        # active_section_schema_manager.get_header_rmy(record)
        month_list = map(util.month_to_int, util.transform_to_months(header_rmy))  # f"Q{header_rmy[-1:]}"))
        rpt_month_years = [int(f"{year}{month}") for month in month_list]
        # [int(f"{record['year']}{month}") for month in month_list]  # 202010, 202011, 202012
        print(rpt_month_years)
        # queryset for all records matching test_datafile
        records = []
        err_objs = []
        # active_section_schema_manager.schemas: # TODO: see if we can replace w/ 'models' L35
        for schema in models:
            model = schema.schemas[0].model
            if model == dict: continue  # need a more elegant skip over header/trailer
            # TODO for above, named rowschema/schema manager
            qs = model.objects.filter(datafile=test_cat4_rmy)
            print(qs)
            qs2 = qs.exclude(RPT_MONTH_YEAR__in=rpt_month_years)
            print(qs2)
            if len(qs) > 0:
                records.append(qs)  # evaluate qs, get objects not matching rpt_month_year
        
            for record in records:
                print(record)
                # generate parserError for any records not matching rpt_month_year
                err_objs.append(util.generate_parser_error(
                    schema=schema.schemas[0],
                    line_number=0,  # TODO: can we make this nullable?
                    datafile=test_cat4_rmy,
                    error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                    error_message="RPT_MONTH_YEAR does not match header RPT_MONTH_YEAR",
                    record=record,
                    field="RPT_MONTH_YEAR"
                ))
        [print(err_obj) for err_obj in err_objs]
        x = parse.bulk_create_errors({1: (err_objs)}, len(err_objs), flush=True)
        # check x to ensure bulk_create_errors succeeded

    
    @pytest.mark.django_db
    def test_cat4_tanf_active(self, test_cat4_tanfa, dfs):
        """Run essential checks for TANF/A."""
        print(test_cat4_tanfa)
        x = util.get_text_from_df(test_cat4_tanfa)
        x_prog = x['program_type']
        x_section = x['section']

        models = list((util.get_program_models(x_prog, x_section)).values())
        models.append(header)

        dfs.datafile = test_cat4_tanfa
        dfs.save()

        errors = parse.parse_datafile(test_cat4_tanfa)
        dfs.status = dfs.get_status()
        

        x = util.fiscal_to_calendar(test_cat4_tanfa.year, test_cat4_tanfa.quarter)
        print(x)
        year, header_rmy = x
        # active_section_schema_manager.get_header_rmy(record)
        month_list = map(util.month_to_int, util.transform_to_months(header_rmy))  # f"Q{header_rmy[-1:]}"))
        rpt_month_years = [int(f"{year}{month}") for month in month_list]
        # [int(f"{record['year']}{month}") for month in month_list]  # 202010, 202011, 202012
        print(rpt_month_years)
        # queryset for all records matching test_datafile
        records = []
        err_objs = []

        # active cases
        # TODO: t2 should have matching t1 via case_number and RMY

        cases = tanf.TANF_T1.objects.filter(datafile=test_cat4_tanfa).distinct('CASE_NUMBER')
        for case in cases:
            casefile = active_section.CaseStruct(case.CASE_NUMBER)
            casefile.add_record()    

   

        qs = tanf.TANF_T2.objects.filter(datafile=test_cat4_tanfa)

        ## if we have 100k cases, we'll run 100k queries which is time/resource intensive
        # we can't afford to have these run in the background for a whole week
        for t2 in qs:
            t1 = tanf.TANF_T1.objects.filter(
                datafile=test_cat4_tanfa,
                CASE_NUMBER=t2.CASE_NUMBER,
                RPT_MONTH_YEAR=t2.RPT_MONTH_YEAR
            )
            if len(t1) == 0:
                print("T2 record has no matching T1 record")
                err_objs.append(util.generate_parser_error(
                    schema=tanf.TANF_T2,
                    line_number=0,  # TODO: can we make this nullable?
                    datafile=test_cat4_tanfa,
                    error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                    error_message="T2 record has no matching T1 record",
                    record=t2,
                    field="CASE_NUMBER"
                ))
            else:
                print(f"T2 w/ case {t2.CASE_NUMBER} has matching T1")

        assert False
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
    

