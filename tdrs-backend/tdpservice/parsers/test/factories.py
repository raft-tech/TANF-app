"""Factories for generating test data for parsers."""
import factory
from tdpservice.data_files.test.factories import DataFileFactory

class ParserErrorFactory(factory.django.DjangoModelFactory):
    """Generate test data for parser errors."""

    class Meta:
        """Hardcoded meta data for parser errors."""

        model = "parsers.ParserError"

    file = factory.SubFactory(DataFileFactory)
    row_number = 1
    column_number = "1"
    item_number = "1"
    field_name = "test field name"
    case_number = '1'
    rpt_month_year = 202001
    error_message = "test error message"
    error_type = "out of range"

    created_at = factory.Faker("date_time")
    fields_json = {"test": "test"}

    object_id = 1
    content_type_id = 1

class TanfT4Factory(factory.django.DjangoModelFactory):
    """Generate TANF T4 record for testing."""

    class Meta:
        """Hardcoded meta data for TANF_T4."""

        model = "search_indexes.TANF_T4"

    RPT_MONTH_YEAR = 202301
    CASE_NUMBER = "1"

    COUNTY_FIPS_CODE = 1
    STRATUM = 1
    ZIP_CODE = "11111"
    DISPOSITION = 1
    CLOSURE_REASON = 1
    REC_SUB_HOUSING = 1
    REC_MED_ASSIST = 1
    REC_FOOD_STAMPS = 1
    REC_SUB_CC = 1


class TanfT5Factory(factory.django.DjangoModelFactory):
    """Generate TANF T5 record for testing."""

    class Meta:
        """Hardcoded meta data for TANF_T5."""

        model = "search_indexes.TANF_T5"

    RPT_MONTH_YEAR = 202301
    CASE_NUMBER = "1"
    FAMILY_AFFILIATION = 1
    DATE_OF_BIRTH = "02091997"
    SSN = "123456789"
    RACE_HISPANIC = 1
    RACE_AMER_INDIAN = 1
    RACE_ASIAN = 1
    RACE_BLACK = 1
    RACE_HAWAIIAN = 1
    RACE_WHITE = 1
    GENDER = 1
    REC_OASDI_INSURANCE = 1
    REC_FEDERAL_DISABILITY = 1
    REC_AID_TOTALLY_DISABLED = 1
    REC_AID_AGED_BLIND = 1
    REC_SSI = 1
    MARITAL_STATUS = 1
    RELATIONSHIP_HOH = "01"
    PARENT_MINOR_CHILD = 1
    NEEDS_OF_PREGNANT_WOMAN = 1
    EDUCATION_LEVEL = "01"
    CITIZENSHIP_STATUS = 1
    COUNTABLE_MONTH_FED_TIME = "111"
    COUNTABLE_MONTHS_STATE_TRIBE = "11"
    EMPLOYMENT_STATUS = 1
    AMOUNT_EARNED_INCOME = "1"
    AMOUNT_UNEARNED_INCOME = "1"

class TanfT6Factory(factory.django.DjangoModelFactory):
    """Generate TANF T6 record for testing."""

    class Meta:
        """Hardcoded meta data for TANF_T6."""

        model = "search_indexes.TANF_T6"

    CALENDAR_YEAR = 1
    CALENDAR_QUARTER = 1
    NUM_APPLICATIONS = 1
    NUM_APPROVED = 1
    NUM_DENIED = 1
    NUM_ASSISTANCE = 1
    NUM_FAMILIES = 1
    NUM_2_PARENTS = 1
    NUM_1_PARENTS = 1
    NUM_NO_PARENTS = 1
    NUM_RECIPIENTS = 1
    NUM_ADULT_RECIPIENTS = 1
    NUM_CHILD_RECIPIENTS = 1
    NUM_NONCUSTODIALS = 1
    NUM_BIRTHS = 1
    NUM_OUTWEDLOCK_BIRTHS = 1
    NUM_CLOSED_CASES = 1
