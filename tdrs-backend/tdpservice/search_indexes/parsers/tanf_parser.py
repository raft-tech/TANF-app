"""Transforms a TANF datafile into an search_index model."""

from ..models import T1, T2, T3, T4, T5, T6, T7, ParserLog
from .preparser import get_row_type

class Field:
    """Provides a mapping between a field name and its position."""
    def __init__(self, name, length, start, end):
        self.name = name
        self.length = length
        self.start = start
        self.end = end

    def create(self, name, length, start, end):
        """Create a new field."""
        return Field(name, length, start, end)

    def __repr__(self):
        return f"{self.name}({self.start}-{self.end})"

class RowSchema:
    """Maps the schema for data rows."""

    def __init__(self, section):
        self.fields = []
        self.section = section # intended for future use with multiple section objects


    def add_field(self, name, length, start, end):
        """Add a field to the schema."""

        self.fields.append(
            Field(name, length, start, end)
        )

    def add_fields(self, fields:list):
        """Add multiple fields to the schema."""
        for field in fields:
            self.add_field(field)

    def get_field(self, name):
        """Get a field from the schema."""
        return self.fields[name]

    def get_field_names(self):
        """Get all field names from the schema."""
        return self.fields.keys()

    def get_all_fields(self):
        """Get all fields from the schema."""
        return self.fields


def active_case_data(datafile):
    """Parses active case data."""

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
    # split line into fields
    family_case_schema = RowSchema()
    family_case_schema.add_fields(
        [
            ('record_type', 2, 1, 2), # does it make sense to try to include regex here as fifth =r'^T1$'
            ('reporting_month', 6, 3, 8),
            ('case_number', 11, 9, 19),
            ('county_fips_code', 3, 20, 22),
            ('stratum', 2, 23, 24),
            ('zip_code', 5, 25, 29),
            ('funding_stream', 1, 30, 30),
            ('disposition', 1, 31, 31),
            ('new_applicant', 1, 32, 32),
            ('family_members', 2, 33, 34),
            ('type_of_family', 1, 35, 35),
            ('subsidized_housing', 1, 36, 36),
            ('medical_assistance', 1, 37, 37),
            ('food_stamps', 1, 38, 38),
            ('food_stamp_amount', 4, 39, 42),
            ('sub_child_care', 1, 43, 43),
            ('amt_child_care', 4, 44, 47),
            ('amt_chiild_support', 4, 48, 51),
            ('families_cash', 4, 52, 55),
            ('cash_amount', 4, 56, 59),
            ('cash_nbr_month', 3, 60, 62),
            ('tanf_child_care_amount', 4, 63, 66),
            ('children_covered', 2, 67, 68),
            ('child_care_nbr_months', 3, 69, 71),
            ('transportation_amount', 4, 72, 75),
            ('transport_nbr_months', 3, 76, 78),
            ('transitional_services_amount', 4, 79, 82),
            ('transitional_nbr_months', 3, 83, 85),
            ('other_amount', 4, 86, 89),
            ('other_nbr_months', 3, 90, 92),
            ('reduction_amt', 4, 93, 96),
            ('reduc_work_req', 1, 97, 97),
            ('reduc_no_diploma', 1, 98, 98),
            ('reduc_not_in_school', 1, 99, 99),
            ('reduc_not_child_support', 1, 100, 100),
            ('reduc_irp_failure', 1, 101, 101),
            ('reduc_other_sanction', 1, 102, 102),
            ('reduc_prior_overpayment', 4, 103, 106),
            ('total_reduc_amount', 4, 107, 110),
            ('reduc_family_cap', 1, 111, 111),
            ('reduc_length_of_assist', 1, 112, 112),
            ('other_non_sanction', 1, 113, 113),
            ('waiver_control_grps', 1, 114, 114),
            ('tanf_family_exempt_time_limits', 2, 115, 116),
            ('child_only_family', 1, 117, 117),
            ('blank', 39, 118, 156),
        ]
    )

    with open(datafile, 'r') as f:
        for line in f:
            # create search_index model
            t1 = T1()
            for field in family_case_schema.get_all_fields():
                setattr(t1, field.name, line[field.start:field.end])

            
                '''
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
            
            try:
                t1.is_valid() # I think I need this to be full_clean()
                t1.save()
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
                 





# TODO: def closed_case_data(datafile):

# TODO: def aggregate_data(datafile):

# TODO: def stratum_data(datafile):

def parse(datafile, section):
    """Parse the datafile into the search_index model."""

    if section == 'active_case_data':
        active_case_data(datafile)
    elif section == 'closed_case_data':
        closed_case_data(datafile)
    elif section == 'aggregate_data':
        aggregate_data(datafile)
    elif section == 'stratum_data':
        stratum_data(datafile)
    else:
        raise ValueError('Invalid section: {}'.format(section))


            

