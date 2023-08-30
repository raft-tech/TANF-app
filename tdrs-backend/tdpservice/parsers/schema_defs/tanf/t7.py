"""Schema for TANF T7 Row."""

from ...util import SchemaManager
from ...fields import Field, TransformField
from ...row_schema import RowSchema
from ...transforms import calendar_quarter_to_rpt_month_year
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
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=7, endIndex=8,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=8, endIndex=10,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=10, endIndex=17,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s2 = RowSchema(
    model=TANF_T7,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(7, 31),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=7, endIndex=8,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=8, endIndex=10,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=17, endIndex=24,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s3 = RowSchema(
    model=TANF_T7,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(7, 31),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=7, endIndex=8,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=8, endIndex=10,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=24, endIndex=31,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s4 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(31, 55),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=31, endIndex=32,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=32, endIndex=34,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=34, endIndex=41,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s5 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(31, 55),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=31, endIndex=32,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=32, endIndex=34,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=41, endIndex=48,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s6 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(31, 55),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=31, endIndex=32,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=32, endIndex=34,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=48, endIndex=55,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s7 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(55, 79),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=55, endIndex=56,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=56, endIndex=58,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=58, endIndex=65,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s8 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(55, 79),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=55, endIndex=56,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=56, endIndex=58,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=65, endIndex=72,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s9 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(55, 79),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=55, endIndex=56,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=56, endIndex=58,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=72, endIndex=79,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)


s10 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(79, 103),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=79, endIndex=80,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=80, endIndex=82,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=82, endIndex=89,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s11 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(79, 103),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=79, endIndex=80,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=80, endIndex=82,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=89, endIndex=96,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s12 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(79, 103),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=79, endIndex=80,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=80, endIndex=82,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=96, endIndex=103,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)


s13 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(103, 127),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=103, endIndex=104,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=104, endIndex=106,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=106, endIndex=113,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s14 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(103, 127),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=103, endIndex=104,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=104, endIndex=106,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=113, endIndex=120,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s15 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(103, 127),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=103, endIndex=104,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=104, endIndex=106,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=120, endIndex=127,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)


s16 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(127, 151),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=127, endIndex=128,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=128, endIndex=130,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=130, endIndex=137,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s17 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(127, 151),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=127, endIndex=128,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=128, endIndex=130,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=137, endIndex=144,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s18 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(127, 151),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=127, endIndex=128,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=128, endIndex=130,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=144, endIndex=151,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)


s19 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(151, 175),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=151, endIndex=152,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=152, endIndex=154,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=154, endIndex=161,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s20 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(151, 175),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=151, endIndex=152,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=152, endIndex=154,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=161, endIndex=168,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s21 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(151, 175),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=151, endIndex=152,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=152, endIndex=154,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=168, endIndex=175,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s22 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(175, 199),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=175, endIndex=176,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=176, endIndex=178,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=178, endIndex=185,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s23 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(175, 199),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=175, endIndex=176,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=176, endIndex=178,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=185, endIndex=192,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s24 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(175, 199),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=175, endIndex=176,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=176, endIndex=178,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=192, endIndex=199,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)


s25 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(199, 223),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=199, endIndex=200,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=200, endIndex=202,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=202, endIndex=209,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s26 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(199, 223),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=199, endIndex=200,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=200, endIndex=202,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=209, endIndex=216,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s27 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(199, 223),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=199, endIndex=200,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=200, endIndex=202,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=216, endIndex=223,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)


s28 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(223, 247),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="40", name='TDRS_SECTION_IND', type='string', startIndex=223, endIndex=224,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="50", name='STRATUM', type='string', startIndex=224, endIndex=226,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6A0", name='FAMILIES_MONTH', type='number', startIndex=226, endIndex=233,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s29 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(223, 247),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=223, endIndex=224,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=224, endIndex=226,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6B", name='FAMILIES_MONTH', type='number', startIndex=233, endIndex=240,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)

s30 = RowSchema(
    model=TANF_T7,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(0, 7),
        validators.notEmpty(223, 247),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="3A", name='RPT_MONTH_YEAR', type='number',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=223, endIndex=224,
              required=True, validators=[validators.oneOf(['1', '2'])]),
        Field(item="5", name='STRATUM', type='string', startIndex=224, endIndex=226,
              required=True, validators=[validators.isInStringRange(1, 99)]),
        Field(item="6C", name='FAMILIES_MONTH', type='number', startIndex=240, endIndex=247,
              required=True, validators=[validators.isInLimits(0, 9999999)]),
    ]
)


t7 = SchemaManager(schemas=[s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16,
                            s17, s18, s19, s20, s21, s22, s23, s24, s25, s26, s27, s28, s29, s30])
