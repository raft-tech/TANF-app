"""Schema for Tribal T6 record."""


from tdpservice.parsers.transforms import calendar_quarter_to_rpt_month_year
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers.validators import category1, category2, category3
from tdpservice.search_indexes.documents.tribal import Tribal_TANF_T6DataSubmissionDocument

s1 = RowSchema(
    record_type="T6",
    document=Tribal_TANF_T6DataSubmissionDocument(),
    preparsing_validators=[
        category1.recordHasLength(379),
        category1.validate_fieldYearMonth_with_headerYearQuarter(),
        category1.calendarQuarterIsValid(2, 7),
    ],
    postparsing_validators=[
        category3.sumIsEqual("NUM_APPLICATIONS", ["NUM_APPROVED", "NUM_DENIED"]),
        category3.sumIsEqual(
            "NUM_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"]
        ),
        category3.sumIsEqual(
            "NUM_RECIPIENTS", ["NUM_ADULT_RECIPIENTS", "NUM_CHILD_RECIPIENTS"]
        ),
    ],
    fields=[
        Field(
            item="0",
            name="RecordType",
            friendly_name="Record Type",
            type="string",
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[],
        ),
        Field(
            item="3",
            name="CALENDAR_QUARTER",
            friendly_name="Calendar Quarter",
            type="number",
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                category2.dateYearIsLargerThan(2019),
                category2.quarterIsValid(),
            ],
        ),
        TransformField(
            calendar_quarter_to_rpt_month_year(0),
            item="4",
            name="RPT_MONTH_YEAR",
            friendly_name="Reporting Year and Month",
            type="number",
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                category2.dateYearIsLargerThan(1998),
                category2.dateMonthIsValid(),
            ],
        ),
        Field(
            item="4A",
            name="NUM_APPLICATIONS",
            friendly_name="Total Number of Applications",
            type="number",
            startIndex=7,
            endIndex=15,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="5A",
            name="NUM_APPROVED",
            friendly_name="Total Number of Approved Applications",
            type="number",
            startIndex=31,
            endIndex=39,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="6A",
            name="NUM_DENIED",
            friendly_name="Total Number of Denied Applications",
            type="number",
            startIndex=55,
            endIndex=63,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="7A",
            name="ASSISTANCE",
            friendly_name="Total Amount of Assistance",
            type="number",
            startIndex=79,
            endIndex=91,
            required=True,
            validators=[category2.isBetween(0, 999999999999, inclusive=True)],
        ),
        Field(
            item="8A",
            name="NUM_FAMILIES",
            friendly_name="Total Number of Families",
            type="number",
            startIndex=115,
            endIndex=123,
            required=True,
            validators=[category2.isBetween(1, 99999999, inclusive=True)],
        ),
        Field(
            item="9A",
            name="NUM_2_PARENTS",
            friendly_name="Total Number of Two-parent Families",
            type="number",
            startIndex=139,
            endIndex=147,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="10A",
            name="NUM_1_PARENTS",
            friendly_name="Total Number of One-Parent Families",
            type="number",
            startIndex=163,
            endIndex=171,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="11A",
            name="NUM_NO_PARENTS",
            friendly_name="Total Number of No-Parent Families",
            type="number",
            startIndex=187,
            endIndex=195,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="12A",
            name="NUM_RECIPIENTS",
            friendly_name="Total Number of Recipients",
            type="number",
            startIndex=211,
            endIndex=219,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="13A",
            name="NUM_ADULT_RECIPIENTS",
            friendly_name="Total Number of Adult Recipients",
            type="number",
            startIndex=235,
            endIndex=243,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="14A",
            name="NUM_CHILD_RECIPIENTS",
            friendly_name="Total Number of Child Recipients",
            type="number",
            startIndex=259,
            endIndex=267,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="15A",
            name="NUM_NONCUSTODIALS",
            friendly_name="Total Number of Noncustodial Parents Participating in Work Activities",
            type="number",
            startIndex=283,
            endIndex=291,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="16A",
            name="NUM_BIRTHS",
            friendly_name="Total Number of Births",
            type="number",
            startIndex=307,
            endIndex=315,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="17A",
            name="NUM_OUTWEDLOCK_BIRTHS",
            friendly_name="Total Number of Out-of-Wedlock Births",
            type="number",
            startIndex=331,
            endIndex=339,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="18A",
            name="NUM_CLOSED_CASES",
            friendly_name="Total Number of Closed Cases",
            type="number",
            startIndex=355,
            endIndex=363,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
    ],
)

s2 = RowSchema(
    record_type="T6",
    document=Tribal_TANF_T6DataSubmissionDocument(),
    quiet_preparser_errors=True,
    preparsing_validators=[
        category1.recordHasLength(379),
        category1.validate_fieldYearMonth_with_headerYearQuarter(),
        category1.calendarQuarterIsValid(2, 7),
    ],
    postparsing_validators=[
        category3.sumIsEqual("NUM_APPLICATIONS", ["NUM_APPROVED", "NUM_DENIED"]),
        category3.sumIsEqual(
            "NUM_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"]
        ),
        category3.sumIsEqual(
            "NUM_RECIPIENTS", ["NUM_ADULT_RECIPIENTS", "NUM_CHILD_RECIPIENTS"]
        ),
    ],
    fields=[
        Field(
            item="0",
            name="RecordType",
            friendly_name="Record Type",
            type="string",
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[],
        ),
        Field(
            item="3",
            name="CALENDAR_QUARTER",
            friendly_name="Calendar Quarter",
            type="number",
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                category2.dateYearIsLargerThan(2019),
                category2.quarterIsValid(),
            ],
        ),
        TransformField(
            calendar_quarter_to_rpt_month_year(1),
            item="4",
            name="RPT_MONTH_YEAR",
            friendly_name="Reporting Year and Month",
            type="number",
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[],
        ),
        Field(
            item="4B",
            name="NUM_APPLICATIONS",
            friendly_name="Total Number of Applications",
            type="number",
            startIndex=15,
            endIndex=23,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="5B",
            name="NUM_APPROVED",
            friendly_name="Total Number of Approved Applications",
            type="number",
            startIndex=39,
            endIndex=47,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="6B",
            name="NUM_DENIED",
            friendly_name="Total Number of Denied Applications",
            type="number",
            startIndex=63,
            endIndex=71,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="7B",
            name="ASSISTANCE",
            friendly_name="Total Amount of Assistance",
            type="number",
            startIndex=91,
            endIndex=103,
            required=True,
            validators=[category2.isBetween(0, 999999999999, inclusive=True)],
        ),
        Field(
            item="8B",
            name="NUM_FAMILIES",
            friendly_name="Total Number of Families",
            type="number",
            startIndex=123,
            endIndex=131,
            required=True,
            validators=[category2.isBetween(1, 99999999, inclusive=True)],
        ),
        Field(
            item="9B",
            name="NUM_2_PARENTS",
            friendly_name="Total Number of Two-parent Families",
            type="number",
            startIndex=147,
            endIndex=155,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="10B",
            name="NUM_1_PARENTS",
            friendly_name="Total Number of One-Parent Families",
            type="number",
            startIndex=171,
            endIndex=179,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="11B",
            name="NUM_NO_PARENTS",
            friendly_name="Total Number of No-Parent Families",
            type="number",
            startIndex=195,
            endIndex=203,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="12B",
            name="NUM_RECIPIENTS",
            friendly_name="Total Number of Recipients",
            type="number",
            startIndex=219,
            endIndex=227,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="13B",
            name="NUM_ADULT_RECIPIENTS",
            friendly_name="Total Number of Adult Recipients",
            type="number",
            startIndex=243,
            endIndex=251,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="14B",
            name="NUM_CHILD_RECIPIENTS",
            friendly_name="Total Number of Child Recipients",
            type="number",
            startIndex=267,
            endIndex=275,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="15B",
            name="NUM_NONCUSTODIALS",
            friendly_name="Total Number of Noncustodial Parents Participating in Work Activities",
            type="number",
            startIndex=291,
            endIndex=299,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="16B",
            name="NUM_BIRTHS",
            friendly_name="Total Number of Births",
            type="number",
            startIndex=315,
            endIndex=323,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="17B",
            name="NUM_OUTWEDLOCK_BIRTHS",
            friendly_name="Total Number of Out-of-Wedlock Births",
            type="number",
            startIndex=339,
            endIndex=347,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="18B",
            name="NUM_CLOSED_CASES",
            friendly_name="Total Number of Closed Cases",
            type="number",
            startIndex=363,
            endIndex=371,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
    ],
)

s3 = RowSchema(
    record_type="T6",
    document=Tribal_TANF_T6DataSubmissionDocument(),
    quiet_preparser_errors=True,
    preparsing_validators=[
        category1.recordHasLength(379),
        category1.validate_fieldYearMonth_with_headerYearQuarter(),
        category1.calendarQuarterIsValid(2, 7),
    ],
    postparsing_validators=[
        category3.sumIsEqual("NUM_APPLICATIONS", ["NUM_APPROVED", "NUM_DENIED"]),
        category3.sumIsEqual(
            "NUM_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"]
        ),
        category3.sumIsEqual(
            "NUM_RECIPIENTS", ["NUM_ADULT_RECIPIENTS", "NUM_CHILD_RECIPIENTS"]
        ),
    ],
    fields=[
        Field(
            item="0",
            name="RecordType",
            friendly_name="Record Type",
            type="string",
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[],
        ),
        Field(
            item="3",
            name="CALENDAR_QUARTER",
            friendly_name="Calendar Quarter",
            type="number",
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                category2.dateYearIsLargerThan(2019),
                category2.quarterIsValid(),
            ],
        ),
        TransformField(
            calendar_quarter_to_rpt_month_year(2),
            item="4",
            name="RPT_MONTH_YEAR",
            friendly_name="Reporitng Year and Month",
            type="number",
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[],
        ),
        Field(
            item="4C",
            name="NUM_APPLICATIONS",
            friendly_name="Total Number of Applications",
            type="number",
            startIndex=23,
            endIndex=31,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="5C",
            name="NUM_APPROVED",
            friendly_name="Total Number of Approved Applications",
            type="number",
            startIndex=47,
            endIndex=55,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="6C",
            name="NUM_DENIED",
            friendly_name="Total Number of Denied Applications",
            type="number",
            startIndex=71,
            endIndex=79,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="7C",
            name="ASSISTANCE",
            friendly_name="Total Amount of Assistance",
            type="number",
            startIndex=103,
            endIndex=115,
            required=True,
            validators=[category2.isBetween(0, 999999999999, inclusive=True)],
        ),
        Field(
            item="8C",
            name="NUM_FAMILIES",
            friendly_name="Total Number of Families",
            type="number",
            startIndex=131,
            endIndex=139,
            required=True,
            validators=[category2.isBetween(1, 99999999, inclusive=True)],
        ),
        Field(
            item="9C",
            name="NUM_2_PARENTS",
            friendly_name="Total Number of Two-parent Families",
            type="number",
            startIndex=155,
            endIndex=163,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="10C",
            name="NUM_1_PARENTS",
            friendly_name="Total Number of One-parent Families",
            type="number",
            startIndex=179,
            endIndex=187,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="11C",
            name="NUM_NO_PARENTS",
            friendly_name="Total Number of No-parent Families",
            type="number",
            startIndex=203,
            endIndex=211,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="12C",
            name="NUM_RECIPIENTS",
            friendly_name="Total Number of Recipients",
            type="number",
            startIndex=227,
            endIndex=235,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="13C",
            name="NUM_ADULT_RECIPIENTS",
            friendly_name="Total Number of Adult Recipients",
            type="number",
            startIndex=251,
            endIndex=259,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="14C",
            name="NUM_CHILD_RECIPIENTS",
            friendly_name="Total Number of Child Recipients",
            type="number",
            startIndex=275,
            endIndex=283,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="15C",
            name="NUM_NONCUSTODIALS",
            friendly_name="Total Number of Noncustodial Parents Participating in Work Activities",
            type="number",
            startIndex=299,
            endIndex=307,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="16C",
            name="NUM_BIRTHS",
            friendly_name="Total Number of Births",
            type="number",
            startIndex=323,
            endIndex=331,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="17C",
            name="NUM_OUTWEDLOCK_BIRTHS",
            friendly_name="Total Number of Out-of-Wedlock Births",
            type="number",
            startIndex=347,
            endIndex=355,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
        Field(
            item="18C",
            name="NUM_CLOSED_CASES",
            friendly_name="Total Number of Closed Cases",
            type="number",
            startIndex=371,
            endIndex=379,
            required=True,
            validators=[category2.isBetween(0, 99999999, inclusive=True)],
        ),
    ],
)


t6 = SchemaManager(schemas=[s1, s2, s3])
