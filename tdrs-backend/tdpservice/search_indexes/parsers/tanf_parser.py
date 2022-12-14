"""Transforms a TANF datafile into an search_index model."""

import logging
from ..models import T1  # , T2, T3, T4, T5, T6, T7, ParserLog
# from django.core.exceptions import ValidationError
from .util import get_record_type

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Field:
    """Provides a mapping between a field name and its position."""

    def __init__(self, name, length, start, end, type):
        self.name = name
        self.length = length
        self.start = start
        self.end = end
        self.type = type

    def create(self, name, length, start, end, type):
        """Create a new field."""
        return Field(name, length, start, end, type)

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.start}-{self.end})"

class RowSchema:
    """Maps the schema for data rows."""

    def __init__(self):  # , section):
        self.fields = []
        # self.section = section # intended for future use with multiple section objects

    def add_field(self, name, length, start, end, type):
        """Add a field to the schema."""
        self.fields.append(
            Field(name, length, start, end, type)
        )

    def add_fields(self, fields: list):
        """Add multiple fields to the schema."""
        for field, length, start, end, type in fields:
            self.add_field(field, length, start, end, type)

    def get_field(self, name):
        """Get a field from the schema."""
        return self.fields[name]

    def get_field_names(self):
        """Get all field names from the schema."""
        return self.fields.keys()

    def get_all_fields(self):
        """Get all fields from the schema."""
        return self.fields


def active_t1(line):
    """Parse row as active case data, T1 only."""
    '''
                    FAMILY CASE CHARACTERISTIC DATA

    DESCRIPTION         LENGTH  FROM    TO  COMMENTS
    RECORD TYPE         2       1       2   "T1" - SECTION 1
    REPORTING MONTH     6       3       8   Numeric
    CASE NUMBER         11      9       19  Alphanumeric
    COUNTY FIPS CODE    3       20      22  Numeric
    STRATUM             2       23      24  Numeric
    ZIP CODE            5       25      29  Alphanumeric
    FUNDING STREAM      1       30      30  Numeric
    DISPOSITION         1       31      31  Numeric
    NEW APPLICANT       1       32      32  Numeric
    FAMILY MEMBERS      2       33      34  Numeric
    TYPE OF FAMILY      1       35      35  Numeric
    SUBSIDIZED HOUSING  1       36      36  Numeric
    MEDICAL ASSISTANCE  1       37      37  Numeric
    FOOD STAMPS         1       38      38  Numeric
    FOOD STAMP AMOUNT   4       39      42  Numeric
    SUB CHILD CARE      1       43      43  Numeric
    AMT CHILD CARE      4       44      47  Numeric
    AMT CHIILD SUPPORT  4       48      51  Numeric
    FAMILY'S CASH       4       52      55  Numeric
    CASH
    AMOUNT              4       56      59  Numeric
    NBR_MONTH           3       60      62  Numeric
    TANF CHILD CARE
    AMOUNT              4       63      66  Numeric
    CHILDREN_COVERED    2       67      68  Numeric
    NBR_MONTHS          3       69      71  Numeric
    TRANSPORTATION
    AMOUNT              4       72      75  Numeric
    NBR_MONTHS          3       76      78  Numeric
    TRANSITIONAL SERVICES
    AMOUNT              4       79      82  Numeric
    NBR_MONTHS          3       83      85  Numeric
    OTHER
    AMOUNT              4       86      89  Numeric
    NBR_MONTHS          3       90      92  Numeric
    REASON FOR & AMOUNT OF ASSISTANCE
    REDUCTION
    SANCTIONS AMT       4       93      96  Numeric
    WORK REQ            1       97      97  Alphanumeric
    NO DIPLOMA          1       98      98  Alphanumeric
    NOT IN SCHOOL       1       99      99  Alphanumeric
    NOT CHILD SUPPORT   1       100     100 Alphanumeric
    IRP FAILURE         1       101     101 Alphanumeric
    OTHER SANCTION      1       102     102 Alphanumeric
    PRIOR OVERPAYMENT   4       103     106 Alphanumeric
    TOTAL REDUC AMOUNT  4       107     110 Alphanumeric
    FAMILY CAP          1       111     111 Alphanumeric
    LENGTH OF ASSIST    1       112     112 Alphanumeric
    OTHER, NON-SANCTION 1       113     113 Alphanumeric
    WAIVER_CONTROL_GRPS 1       114     114 Alphanumeric
    TANF FAMILY
    EXEMPT TIME_LIMITS  2       115     116 Numeric
    CHILD ONLY FAMILY   1       117     117 Numeric
    BLANK               39      118     156 Spaces
    '''

    # all of the below is assumed T1, we will eventually expand this for other sections
    # via get_record_type(line)

    # split line into fields
    family_case_schema = RowSchema()
    family_case_schema.add_fields(
        [  # does it make sense to try to include regex (e.g., =r'^T1$')
            ('record_type', 2, 1, 2, "Alphanumeric"),
            ('reporting_month', 6, 3, 8, "Numeric"),
            ('case_number', 11, 9, 19, "Alphanumeric"),
            ('county_fips_code', 3, 20, 22, "Numeric"),
            ('stratum', 2, 23, 24, "Numeric"),
            ('zip_code', 5, 25, 29, "Alphanumeric"),
            ('funding_stream', 1, 30, 30, "Numeric"),
            ('disposition', 1, 31, 31, "Numeric"),
            ('new_applicant', 1, 32, 32, "Numeric"),
            ('family_size', 2, 33, 34, "Numeric"),
            ('family_type', 1, 35, 35, "Numeric"),
            ('receives_sub_housing', 1, 36, 36, "Numeric"),
            ('receives_medical_assistance', 1, 37, 37, "Numeric"),
            ('receives_food_stamps', 1, 38, 38, "Numeric"),
            ('food_stamp_amount', 4, 39, 42, "Numeric"),
            ('receives_sub_child_care', 1, 43, 43, "Numeric"),
            ('child_care_amount', 4, 44, 47, "Numeric"),
            ('child_support_amount', 4, 48, 51, "Numeric"),
            ('family_cash_recources', 4, 52, 55, "Numeric"),
            ('family_cash_amount', 4, 56, 59, "Numeric"),
            ('family_cash_nbr_month', 3, 60, 62, "Numeric"),
            ('tanf_child_care_amount', 4, 63, 66, "Numeric"),
            ('children_covered', 2, 67, 68, "Numeric"),
            ('child_care_nbr_months', 3, 69, 71, "Numeric"),
            ('transportation_amount', 4, 72, 75, "Numeric"),
            ('transport_nbr_months', 3, 76, 78, "Numeric"),
            ('transition_services_amount', 4, 79, 82, "Numeric"),
            ('transition_nbr_months', 3, 83, 85, "Numeric"),
            ('other_amount', 4, 86, 89, "Numeric"),
            ('other_nbr_months', 3, 90, 92, "Numeric"),
            ('reduction_amount', 4, 93, 96, "Numeric"),
            ('reduc_work_requirements', 1, 97, 97, "Numeric"),
            ('reduc_adult_no_hs_diploma', 1, 98, 98, "Numeric"),
            ('reduc_teen_not_in_school', 1, 99, 99, "Numeric"),
            ('reduc_noncooperation_child_support', 1, 100, 100, "Numeric"),
            ('reduc_irp_failure', 1, 101, 101, "Numeric"),
            ('reduc_other_sanction', 1, 102, 102, "Numeric"),
            ('reduc_prior_overpayment', 4, 103, 106, "Numeric"),
            ('total_reduc_amount', 4, 107, 110, "Numeric"),
            ('reduc_family_cap', 1, 111, 111, "Numeric"),
            ('reduc_length_of_assist', 1, 112, 112, "Numeric"),
            ('other_non_sanction', 1, 113, 113, "Numeric"),
            ('waiver_control_grps', 1, 114, 114, "Numeric"),
            ('tanf_family_exempt_time_limits', 2, 115, 116, "Numeric"),
            ('tanf_new_child_only_family', 1, 117, 117, "Numeric"),
            ('blank', 39, 118, 156, "Spaces"),
        ]
    )

    # create search_index model
    t1 = T1()
    content_is_valid = True
    for field in family_case_schema.get_all_fields():
        if field.name == 'blank':
            break
        content = line[field.start-1:field.end]  # descriptor pdfs were off by one, could also adjust start values
        if len(content) != field.length:
            logger.warn('Expected field "%s" with length %d, got: "%s"', field.name, field.length, content)
            content_is_valid = False
            continue
        # check if content is type string or integer
        if field.type == 'Numeric':
            try:
                content = int(content)
            except ValueError:
                logger.warn('Expected field "%s" to be numeric, got: "%s"', field.name, content)
                content_is_valid = False
                continue
        elif field.type == 'Alphanumeric':
            pass  # maybe we can regex check some of these later
        # The below is extremely spammy, turn on selectively.
        # logger.debug('field: %s\t::content: "%s"\t::end: %s', field.name, content, field.end)

        if content_is_valid:
            setattr(t1, field.name, content)

    if not content_is_valid:
        logger.warn('Content is not valid, skipping model creation.')
        return

        '''
        Old manual parsing w/o helper classes
        reporting_month=line[2:8],
        case_number=line[8:19],
        county_fips_code=line[19:22],
        stratum=line[22:24],
        zip_code=line[24:29],
        funding_stream=line[29:30],
        disposition=line[30:31],
        new_applicant=line[31:32],
        family_members=line[32:34],
        type_of_family=line[34:35],
        subsidized_housing=line[35:36],
        medical_assistance=line[36:37],
        food_stamps=line[37:38],
        food_stamp_amount=line[38:42],
        sub_child_care=line[42:43],
        amt_child_care=line[43:47],
        amt_chiild_support=line[47:51],
        family_cash=line[51:55],
        cash_amount=line[55:59],
        nbr_month=line[59:62],
        tanf_child_care_amount=line[62:66],
        children_covered=line[66:68],
        nbr_months=line[68:71],
        transportation_amount=line[71:75],
        nbr_months=line[75:78],
        transitional_services_amount=line[78:82],
        nbr_months=line[82:85],
        other_amount=line[85:89],
        nbr_months=line[89:92],
        reason_for_amount_of_assistance_reduction=line[92:96],
        sanctions_amt=line[96:97],
        work_req=line[97:98],
        no_diploma=line[98:99],
        not_in_school=line[99:100],
        not_child_support=line[100:101],
        irp_failure=line[101:102],
        other_sanction=line[102:103],
        prior_overpayment=line[103:106],
        total_reduc_amount=line[106:110],
        family_cap=line[110:111],
        length_of_assist=line[111:112],
        other_non_sanction=line[112:113],
        waiver_control_grps=line[113:114],
        tanf_family_exempt_time_limits=line[114:116],
        child_only_family=line[116:117],
        blank=line[117:156],
    )
        '''

    # try:
    # t1.full_clean()
    logger.info("about to run t1.save")
    t1.save()
    '''
    # holdovers for 1354
        ParserLog.objects.create(
            data_file=datafile,
            status=ParserLog.Status.ACCEPTED,
        )

    except ValidationError as e:
        return ParserLog.objects.create(
            data_file=datafile,
            status=ParserLog.Status.ACCEPTED_WITH_ERRORS,
            errors=e.message
        )
    '''

# TODO: def closed_case_data(datafile):

# TODO: def aggregate_data(datafile):

# TODO: def stratum_data(datafile):

def parse(datafile):
    """Parse the datafile into the search_index model."""
    logger.info('Parsing TANF datafile: %s', datafile)

    datafile.seek(0)  # ensure we are at the beginning of the file
    for raw_line in datafile:
        logger.debug('Parsing this line: "%s"', raw_line)
        if isinstance(raw_line, bytes):
            logger.info("Line is bytes, decoding to string...")
            raw_line = raw_line.decode()
        line = raw_line.strip('\r\n')

        record_type = get_record_type(line)
        logger.debug('Parsing as type %s this line: "%s"', record_type, line)

        if record_type == 'HE':
            # Headers do not differ between types, this is part of preparsing.
            continue
        elif record_type == 'T1':
            expected_line_length = 156  # we will need to adjust for other types
            actual_line_length = len(line)
            logger.debug('Expected line length of 156, got: %s', actual_line_length)
            if actual_line_length != expected_line_length:
                logger.error('Expected line length of 156, got: %s', actual_line_length)
                # should be added to parser log in #1354
                continue
            else:
                active_t1(line)
        else:
            logger.warn("Parsing for type %s not yet implemented", record_type)
            continue
