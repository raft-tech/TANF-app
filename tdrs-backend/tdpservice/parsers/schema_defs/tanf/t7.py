"""Schema for TANF T7 Row."""

from ...util import SchemaManager
from ...fields import Field
from ...row_schema import RowSchema
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T7


s1 = RowSchema(
    model=TANF_T7,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(7, 31),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3A", name='CALENDAR_YEAR', type='number', startIndex=2, endIndex=6,
              required=True, validators=[validators.month_year_yearIsLargerThan(1998)]),
        Field(item="3B", name='CALENDAR_QUARTER', type='number', startIndex=6, endIndex=7,
              required=True, validators=[validators.isInLimits(1, 4)]),
        Field(item="4_1", name='TDRS_SECTION_IND', type='string', startIndex=7, endIndex=8,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5_1", name='STRATUM', type='string', startIndex=8, endIndex=10,
              required=True, validators=[validators.isInStringRange(1, 99),]),
        Field(item="6A_1", name='FAMILIES_MONTH_1', type='number', startIndex=10, endIndex=17,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
        Field(item="6B_1", name='FAMILIES_MONTH_2', type='number', startIndex=17, endIndex=24,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
        Field(item="6C_1", name='FAMILIES_MONTH_3', type='number', startIndex=24, endIndex=31,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s2 = RowSchema(
    model=TANF_T7,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(31, 55),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3A", name='CALENDAR_YEAR', type='number', startIndex=2, endIndex=6,
              required=True, validators=[validators.month_year_yearIsLargerThan(1998)]),
        Field(item="3B", name='CALENDAR_QUARTER', type='number', startIndex=6, endIndex=7,
              required=True, validators=[validators.isInLimits(1, 4)]),
        Field(item="4_2", name='TDRS_SECTION_IND', type='string', startIndex=31, endIndex=32,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5_2", name='STRATUM', type='string', startIndex=32, endIndex=34,
              required=True, validators=[validators.isInStringRange(1, 99),]),
        Field(item="6A_2", name='FAMILIES_MONTH_1', type='number', startIndex=34, endIndex=41,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
        Field(item="6B_2", name='FAMILIES_MONTH_2', type='number', startIndex=41, endIndex=48,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
        Field(item="6C_2", name='FAMILIES_MONTH_3', type='number', startIndex=48, endIndex=55,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)


t7 = SchemaManager(schemas=[s1, s2])
