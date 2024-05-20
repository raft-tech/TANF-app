"""Schema for t1 record types."""

from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers import validators
from tdpservice.search_indexes.documents.tanf import TANF_T1DataSubmissionDocument
from tdpservice.parsers.util import generate_t1_t4_hashes


t1 = SchemaManager(
    schemas=[
        RowSchema(
            record_type="T1",
            document=TANF_T1DataSubmissionDocument(),
            generate_hashes_func=generate_t1_t4_hashes,
            preparsing_validators=[
                validators.recordHasLengthBetween(117, 156),
                validators.caseNumberNotEmpty(8, 19),
                validators.or_priority_validators([
                    validators.field_year_month_with_header_year_quarter(),
                    validators.validateRptMonthYear(),
                ]),
            ],
            postparsing_validators=[
                validators.if_then_validator(
                    condition_field_name="CASH_AMOUNT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="NBR_MONTHS",
                    result_function=validators.isLargerThan(0),
                ),
                validators.if_then_validator(
                    condition_field_name="CC_AMOUNT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="CHILDREN_COVERED",
                    result_function=validators.isLargerThan(0),
                ),
                validators.if_then_validator(
                    condition_field_name="CC_AMOUNT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="CC_NBR_MONTHS",
                    result_function=validators.isLargerThan(0),
                ),
                validators.if_then_validator(
                    condition_field_name="TRANSP_AMOUNT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="TRANSP_NBR_MONTHS",
                    result_function=validators.isLargerThan(0),
                ),
                validators.if_then_validator(
                    condition_field_name="TRANSITION_SERVICES_AMOUNT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="TRANSITION_NBR_MONTHS",
                    result_function=validators.isLargerThan(0),
                ),
                validators.if_then_validator(
                    condition_field_name="OTHER_AMOUNT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="OTHER_NBR_MONTHS",
                    result_function=validators.isLargerThan(0),
                ),
                validators.if_then_validator(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="WORK_REQ_SANCTION",
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="FAMILY_SANC_ADULT",
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="SANC_TEEN_PARENT",
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="NON_COOPERATION_CSE",
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="FAILURE_TO_COMPLY",
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="OTHER_SANCTION",
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field_name="OTHER_TOTAL_REDUCTIONS",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="FAMILY_CAP",
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field_name="OTHER_TOTAL_REDUCTIONS",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="REDUCTIONS_ON_RECEIPTS",
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field_name="OTHER_TOTAL_REDUCTIONS",
                    condition_function=validators.isLargerThan(0),
                    result_field_name="OTHER_NON_SANCTION",
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.sumIsLarger(
                    (
                        "AMT_FOOD_STAMP_ASSISTANCE",
                        "AMT_SUB_CC",
                        "CASH_AMOUNT",
                        "CC_AMOUNT",
                        "TRANSP_AMOUNT",
                    ),
                    0,
                ),
            ],
            fields=[
                Field(
                    item="0",
                    name="RecordType",
                    friendly_name="record type",
                    type="string",
                    startIndex=0,
                    endIndex=2,
                    required=True,
                    validators=[],
                ),
                Field(
                    item="4",
                    name="RPT_MONTH_YEAR",
                    friendly_name="reporting month and year",
                    type="number",
                    startIndex=2,
                    endIndex=8,
                    required=True,
                    validators=[
                        validators.dateYearIsLargerThan(1998),
                        validators.dateMonthIsValid(),
                    ],
                ),
                Field(
                    item="6",
                    name="CASE_NUMBER",
                    friendly_name="case number",
                    type="string",
                    startIndex=8,
                    endIndex=19,
                    required=True,
                    validators=[validators.notEmpty()],
                ),
                Field(
                    item="2",
                    name="COUNTY_FIPS_CODE",
                    friendly_name="county fips code",
                    type="string",
                    startIndex=19,
                    endIndex=22,
                    required=True,
                    validators=[
                        validators.isNumber(),
                    ],
                ),
                Field(
                    item="5",
                    name="STRATUM",
                    friendly_name="stratum",
                    type="string",
                    startIndex=22,
                    endIndex=24,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="7",
                    name="ZIP_CODE",
                    friendly_name="zip code",
                    type="string",
                    startIndex=24,
                    endIndex=29,
                    required=True,
                    validators=[
                        validators.isNumber(),
                    ],
                ),
                Field(
                    item="8",
                    name="FUNDING_STREAM",
                    friendly_name="funding stream",
                    type="number",
                    startIndex=29,
                    endIndex=30,
                    required=True,
                    validators=[
                        validators.isInLimits(1, 2),
                    ],
                ),
                Field(
                    item="9",
                    name="DISPOSITION",
                    friendly_name="disposition",
                    type="number",
                    startIndex=30,
                    endIndex=31,
                    required=True,
                    validators=[
                        validators.matches(1)
                    ],
                ),
                Field(
                    item="10",
                    name="NEW_APPLICANT",
                    friendly_name="new applicant",
                    type="number",
                    startIndex=31,
                    endIndex=32,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="11",
                    name="NBR_FAMILY_MEMBERS",
                    friendly_name="number of family members",
                    type="number",
                    startIndex=32,
                    endIndex=34,
                    required=True,
                    validators=[
                        validators.isLargerThan(0),
                    ],
                ),
                Field(
                    item="12",
                    name="FAMILY_TYPE",
                    friendly_name="family type",
                    type="number",
                    startIndex=34,
                    endIndex=35,
                    required=True,
                    validators=[
                        validators.isInLimits(1, 3),
                    ],
                ),
                Field(
                    item="13",
                    name="RECEIVES_SUB_HOUSING",
                    friendly_name="receives subsidized housing",
                    type="number",
                    startIndex=35,
                    endIndex=36,
                    required=True,
                    validators=[
                        validators.isInLimits(1, 2),
                    ],
                ),
                Field(
                    item="14",
                    name="RECEIVES_MED_ASSISTANCE",
                    friendly_name="receives medical assistance",
                    type="number",
                    startIndex=36,
                    endIndex=37,
                    required=True,
                    validators=[
                        validators.isInLimits(1, 2),
                    ],
                ),
                Field(
                    item="15",
                    name="RECEIVES_FOOD_STAMPS",
                    friendly_name="receives food stamps",
                    type="number",
                    startIndex=37,
                    endIndex=38,
                    required=False,
                    validators=[
                        validators.isInLimits(0, 2),
                    ],
                ),
                Field(
                    item="16",
                    name="AMT_FOOD_STAMP_ASSISTANCE",
                    friendly_name="amount of food stamp assistance",
                    type="number",
                    startIndex=38,
                    endIndex=42,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="17",
                    name="RECEIVES_SUB_CC",
                    friendly_name="receives subsidized child care",
                    type="number",
                    startIndex=42,
                    endIndex=43,
                    required=False,
                    validators=[
                        validators.isInLimits(0, 3),
                    ],
                ),
                Field(
                    item="18",
                    name="AMT_SUB_CC",
                    friendly_name="amount of subsidized child care",
                    type="number",
                    startIndex=43,
                    endIndex=47,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="19",
                    name="CHILD_SUPPORT_AMT",
                    friendly_name="child support amount",
                    type="number",
                    startIndex=47,
                    endIndex=51,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="20",
                    name="FAMILY_CASH_RESOURCES",
                    friendly_name="family cash resources",
                    type="number",
                    startIndex=51,
                    endIndex=55,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="21A",
                    name="CASH_AMOUNT",
                    friendly_name="cash amount",
                    type="number",
                    startIndex=55,
                    endIndex=59,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="21B",
                    name="NBR_MONTHS",
                    friendly_name="number of months",
                    type="number",
                    startIndex=59,
                    endIndex=62,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="22A",
                    name="CC_AMOUNT",
                    friendly_name="child care amount",
                    type="number",
                    startIndex=62,
                    endIndex=66,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="22B",
                    name="CHILDREN_COVERED",
                    friendly_name="children covered",
                    type="number",
                    startIndex=66,
                    endIndex=68,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="22C",
                    name="CC_NBR_MONTHS",
                    friendly_name="child care - number of months",
                    type="number",
                    startIndex=68,
                    endIndex=71,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="23A",
                    name="TRANSP_AMOUNT",
                    friendly_name="transportation amount",
                    type="number",
                    startIndex=71,
                    endIndex=75,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="23B",
                    name="TRANSP_NBR_MONTHS",
                    friendly_name="transportation - number of months",
                    type="number",
                    startIndex=75,
                    endIndex=78,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="24A",
                    name="TRANSITION_SERVICES_AMOUNT",
                    friendly_name="transition services amount",
                    type="number",
                    startIndex=78,
                    endIndex=82,
                    required=False,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="24B",
                    name="TRANSITION_NBR_MONTHS",
                    friendly_name="transition services - number of months",
                    type="number",
                    startIndex=82,
                    endIndex=85,
                    required=False,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="25A",
                    name="OTHER_AMOUNT",
                    friendly_name="other amount",
                    type="number",
                    startIndex=85,
                    endIndex=89,
                    required=False,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="25B",
                    name="OTHER_NBR_MONTHS",
                    friendly_name="other - number of months",
                    type="number",
                    startIndex=89,
                    endIndex=92,
                    required=False,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="26AI",
                    name="SANC_REDUCTION_AMT",
                    friendly_name="sanction reduction amount",
                    type="number",
                    startIndex=92,
                    endIndex=96,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="26AII",
                    name="WORK_REQ_SANCTION",
                    friendly_name="work requirement sanction",
                    type="number",
                    startIndex=96,
                    endIndex=97,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26AIII",
                    name="FAMILY_SANC_ADULT",
                    friendly_name="family sanction adult",
                    type="number",
                    startIndex=97,
                    endIndex=98,
                    required=False,
                    validators=[
                        validators.oneOf([0, 1, 2]),
                    ],
                ),
                Field(
                    item="26AIV",
                    name="SANC_TEEN_PARENT",
                    friendly_name="sanctioned teen parent",
                    type="number",
                    startIndex=98,
                    endIndex=99,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26AV",
                    name="NON_COOPERATION_CSE",
                    friendly_name="non-cooperation with child support",
                    type="number",
                    startIndex=99,
                    endIndex=100,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26AVI",
                    name="FAILURE_TO_COMPLY",
                    friendly_name="failure to comply",
                    type="number",
                    startIndex=100,
                    endIndex=101,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26AVII",
                    name="OTHER_SANCTION",
                    friendly_name="other sanction",
                    type="number",
                    startIndex=101,
                    endIndex=102,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26B",
                    name="RECOUPMENT_PRIOR_OVRPMT",
                    friendly_name="recoupment prior overpayment",
                    type="number",
                    startIndex=102,
                    endIndex=106,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="26CI",
                    name="OTHER_TOTAL_REDUCTIONS",
                    friendly_name="other total reductions",
                    type="number",
                    startIndex=106,
                    endIndex=110,
                    required=True,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="26CII",
                    name="FAMILY_CAP",
                    friendly_name="family cap",
                    type="number",
                    startIndex=110,
                    endIndex=111,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26CIII",
                    name="REDUCTIONS_ON_RECEIPTS",
                    friendly_name="reductions on receipts",
                    type="number",
                    startIndex=111,
                    endIndex=112,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26CIV",
                    name="OTHER_NON_SANCTION",
                    friendly_name="other non-sanction",
                    type="number",
                    startIndex=112,
                    endIndex=113,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="27",
                    name="WAIVER_EVAL_CONTROL_GRPS",
                    friendly_name="waiver evaluation control groups",
                    type="string",
                    startIndex=113,
                    endIndex=114,
                    required=False,
                    validators=[
                        validators.oneOf(["9", " "]),
                        validators.isAlphaNumeric(),
                    ],
                ),
                Field(
                    item="28",
                    name="FAMILY_EXEMPT_TIME_LIMITS",
                    friendly_name="family exempt time limits",
                    type="number",
                    startIndex=114,
                    endIndex=116,
                    required=True,
                    validators=[validators.oneOf([1, 2, 3, 4, 6, 7, 8, 9])],
                ),
                Field(
                    item="29",
                    name="FAMILY_NEW_CHILD",
                    friendly_name="family new child",
                    type="number",
                    startIndex=116,
                    endIndex=117,
                    required=False,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="-1",
                    name="BLANK",
                    friendly_name="blank",
                    type="string",
                    startIndex=117,
                    endIndex=156,
                    required=False,
                    validators=[],
                ),
            ],
        )
    ]
)
