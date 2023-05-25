"""Factories for generating test data for parsers."""
import factory
from faker import Faker
from tdpservice.data_files.test.factories import DataFileFactory

fake = Faker()

class ParserErrorFactory(factory.django.DjangoModelFactory):
    """Generate test data for parser errors."""

    class Meta:
        """Hardcoded meta data for parser errors."""

        model = "parsers.ParserError"

    file = factory.SubFactory(DataFileFactory)
    row_number = 1
    column_number = 1
    item_number = 1
    field_name = "test field name"
    category = 1
    case_number = '1'
    rpt_month_year = 202001
    error_message = "test error message"
    error_type = "out of range"

    created_at = factory.Faker("date_time")
    fields_json = {"test": "test"}

    object_id = 1
    content_type_id = 1

class TanfT1Factory(factory.django.DjangoModelFactory):
    """Generate TANF T1 record for testing."""

    class Meta:
        """Hardcoded meta data for TANF_T1."""

        model = "search_indexes.TANF_T1"

    RecordType = fake.uuid4()
    RPT_MONTH_YEAR = 1
    CASE_NUMBER = 1
    COUNTY_FIPS_CODE = 1
    STRATUM = 1
    ZIP_CODE = 1
    FUNDING_STREAM = 1
    DISPOSITION = 1
    NEW_APPLICANT = 1
    NBR_FAMILY_MEMBERS = 1
    FAMILY_TYPE = 1
    RECEIVES_SUB_HOUSING = 1
    RECEIVES_MED_ASSISTANCE = 1
    RECEIVES_FOOD_STAMPS = 1
    AMT_FOOD_STAMP_ASSISTANCE = 1
    RECEIVES_SUB_CC = 1
    AMT_SUB_CC = 1
    CHILD_SUPPORT_AMT = 1
    FAMILY_CASH_RESOURCES = 1
    CASH_AMOUNT = 1
    NBR_MONTHS = 1
    CC_AMOUNT = 1
    CHILDREN_COVERED = 1
    CC_NBR_MONTHS = 1
    TRANSP_AMOUNT = 1
    TRANSP_NBR_MONTHS = 1
    TRANSITION_SERVICES_AMOUNT = 1
    TRANSITION_NBR_MONTHS = 1
    OTHER_AMOUNT = 1
    OTHER_NBR_MONTHS = 1
    SANC_REDUCTION_AMT = 1
    WORK_REQ_SANCTION = 1
    FAMILY_SANC_ADULT = 1
    SANC_TEEN_PARENT = 1
    NON_COOPERATION_CSE = 1
    FAILURE_TO_COMPLY = 1
    OTHER_SANCTION = 1
    RECOUPMENT_PRIOR_OVRPMT = 1
    OTHER_TOTAL_REDUCTIONS = 1
    FAMILY_CAP = 1
    REDUCTIONS_ON_RECEIPTS = 1
    OTHER_NON_SANCTION = 1
    WAIVER_EVAL_CONTROL_GRPS = 1
    FAMILY_EXEMPT_TIME_LIMITS = 1
    FAMILY_NEW_CHILD = 1
