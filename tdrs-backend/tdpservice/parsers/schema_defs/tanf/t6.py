"""Schema for HEADER row of all submission types."""


from tdpservice.parsers.util import SchemaManager
from tdpservice.parsers.transforms import calendar_quarter_to_rpt_month_year
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import RowSchema
from tdpservice.parsers import validators
from tdpservice.search_indexes.models.tanf import TANF_T6


s1 = RowSchema(
    model=TANF_T6,
    preparsing_validators=[
        validators.hasLength(379),
    ],
    postparsing_validators=[
        validators.sumIsEqual("NUM_APPLICATIONS", ["NUM_APPROVED", "NUM_DENIED"]),
        validators.sumIsEqual("NUM_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"]),
        validators.sumIsEqual("NUM_RECIPIENTS", ["NUM_ADULT_RECIPIENTS", "NUM_CHILD_RECIPIENTS"]),
    ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="4", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4A", name='NUM_APPLICATIONS', type='number', startIndex=7, endIndex=15,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="5A", name='NUM_APPROVED', type='number', startIndex=31, endIndex=39,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="6A", name='NUM_DENIED', type='number', startIndex=55, endIndex=63,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="7A", name='ASSISTANCE', type='number', startIndex=79, endIndex=91,
              required=True, validators=[validators.isInLimits(0, 999999999999)]),
        Field(item="8A", name='NUM_FAMILIES', type='number', startIndex=115, endIndex=123,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="9A", name='NUM_2_PARENTS', type='number', startIndex=139, endIndex=147,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="10A", name='NUM_1_PARENTS', type='number', startIndex=163, endIndex=171,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="11A", name='NUM_NO_PARENTS', type='number', startIndex=187, endIndex=195,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="12A", name='NUM_RECIPIENTS', type='number', startIndex=211, endIndex=219,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="13A", name='NUM_ADULT_RECIPIENTS', type='number', startIndex=235, endIndex=243,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="14A", name='NUM_CHILD_RECIPIENTS', type='number', startIndex=259, endIndex=267,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="15A", name='NUM_NONCUSTODIALS', type='number', startIndex=283, endIndex=291,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="16A", name='NUM_BIRTHS', type='number', startIndex=307, endIndex=315,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="17A", name='NUM_OUTWEDLOCK_BIRTHS', type='number', startIndex=331, endIndex=339,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="18A", name='NUM_CLOSED_CASES', type='number', startIndex=355, endIndex=363,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
    ],
)

s2 = RowSchema(
    model=TANF_T6,
    preparsing_validators=[
        validators.hasLength(379),
    ],
    postparsing_validators=[
        validators.sumIsEqual("NUM_APPLICATIONS", ["NUM_APPROVED", "NUM_DENIED"]),
        validators.sumIsEqual("NUM_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"]),
        validators.sumIsEqual("NUM_RECIPIENTS", ["NUM_ADULT_RECIPIENTS", "NUM_CHILD_RECIPIENTS"]),
    ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="4", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[]),
        Field(item="4B", name='NUM_APPLICATIONS', type='number', startIndex=15, endIndex=23,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="5B", name='NUM_APPROVED', type='number', startIndex=39, endIndex=47,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="6B", name='NUM_DENIED', type='number', startIndex=63, endIndex=71,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="7B", name='ASSISTANCE', type='number', startIndex=91, endIndex=103,
              required=True, validators=[validators.isInLimits(0, 999999999999)]),
        Field(item="8B", name='NUM_FAMILIES', type='number', startIndex=123, endIndex=131,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="9B", name='NUM_2_PARENTS', type='number', startIndex=147, endIndex=155,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="10B", name='NUM_1_PARENTS', type='number', startIndex=171, endIndex=179,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="11B", name='NUM_NO_PARENTS', type='number', startIndex=195, endIndex=203,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="12B", name='NUM_RECIPIENTS', type='number', startIndex=219, endIndex=227,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="13B", name='NUM_ADULT_RECIPIENTS', type='number', startIndex=243, endIndex=251,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="14B", name='NUM_CHILD_RECIPIENTS', type='number', startIndex=267, endIndex=275,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="15B", name='NUM_NONCUSTODIALS', type='number', startIndex=291, endIndex=299,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="16B", name='NUM_BIRTHS', type='number', startIndex=315, endIndex=323,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="17B", name='NUM_OUTWEDLOCK_BIRTHS', type='number', startIndex=339, endIndex=347,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="18B", name='NUM_CLOSED_CASES', type='number', startIndex=363, endIndex=371,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
    ],
)

s3 = RowSchema(
    model=TANF_T6,
    preparsing_validators=[
        validators.hasLength(379),
    ],
    postparsing_validators=[
        validators.sumIsEqual("NUM_APPLICATIONS", ["NUM_APPROVED", "NUM_DENIED"]),
        validators.sumIsEqual("NUM_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"]),
        validators.sumIsEqual("NUM_RECIPIENTS", ["NUM_ADULT_RECIPIENTS", "NUM_CHILD_RECIPIENTS"]),
    ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="4", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[]),
        Field(item="4C", name='NUM_APPLICATIONS', type='number', startIndex=23, endIndex=31,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="5C", name='NUM_APPROVED', type='number', startIndex=47, endIndex=55,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="6C", name='NUM_DENIED', type='number', startIndex=71, endIndex=79,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="7C", name='ASSISTANCE', type='number', startIndex=103, endIndex=115,
              required=True, validators=[validators.isInLimits(0, 999999999999)]),
        Field(item="8C", name='NUM_FAMILIES', type='number', startIndex=131, endIndex=139,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="9C", name='NUM_2_PARENTS', type='number', startIndex=155, endIndex=163,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="10C", name='NUM_1_PARENTS', type='number', startIndex=179, endIndex=187,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="11C", name='NUM_NO_PARENTS', type='number', startIndex=203, endIndex=211,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="12C", name='NUM_RECIPIENTS', type='number', startIndex=227, endIndex=235,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="13C", name='NUM_ADULT_RECIPIENTS', type='number', startIndex=251, endIndex=259,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="14C", name='NUM_CHILD_RECIPIENTS', type='number', startIndex=275, endIndex=283,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="15C", name='NUM_NONCUSTODIALS', type='number', startIndex=299, endIndex=307,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="16C", name='NUM_BIRTHS', type='number', startIndex=323, endIndex=331,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="17C", name='NUM_OUTWEDLOCK_BIRTHS', type='number', startIndex=347, endIndex=355,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="18C", name='NUM_CLOSED_CASES', type='number', startIndex=371, endIndex=379,
              required=True, validators=[validators.isInLimits(0, 99999999)]),
    ],
)


t6 = SchemaManager(
      schemas=[
          s1,
          s2,
          s3
      ]
  )
