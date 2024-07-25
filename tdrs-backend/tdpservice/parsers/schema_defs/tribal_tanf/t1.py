"""Schema for Tribal TANF T1 record types."""

from tdpservice.parsers.transforms import zero_pad
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers.validators.category1 import PreparsingValidators
from tdpservice.parsers.validators.category2 import FieldValidators
from tdpservice.parsers.validators.category3 import PostparsingValidators
from tdpservice.search_indexes.documents.tribal import Tribal_TANF_T1DataSubmissionDocument
from tdpservice.parsers.util import generate_t1_t4_hashes, get_t1_t4_partial_hash_members


t1 = SchemaManager(
    schemas=[
        RowSchema(
            record_type="T1",
            document=Tribal_TANF_T1DataSubmissionDocument(),
            generate_hashes_func=generate_t1_t4_hashes,
            get_partial_hash_members_func=get_t1_t4_partial_hash_members,
            preparsing_validators=[
                PreparsingValidators.recordHasLengthBetween(117, 122),
                PreparsingValidators.caseNumberNotEmpty(8, 19),
                PreparsingValidators.or_priority_validators([
                    PreparsingValidators.validate_fieldYearMonth_with_headerYearQuarter(),
                    PreparsingValidators.validateRptMonthYear(),
                ]),
            ],
            postparsing_validators=[
                PostparsingValidators.ifThenAlso(
                    condition_field_name="CASH_AMOUNT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="NBR_MONTHS",
                    result_function=PostparsingValidators.isGreaterThan(0),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="CC_AMOUNT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="CHILDREN_COVERED",
                    result_function=PostparsingValidators.isGreaterThan(0),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="CC_AMOUNT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="CC_NBR_MONTHS",
                    result_function=PostparsingValidators.isGreaterThan(0),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="TRANSP_AMOUNT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="TRANSP_NBR_MONTHS",
                    result_function=PostparsingValidators.isGreaterThan(0),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="TRANSITION_SERVICES_AMOUNT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="TRANSITION_NBR_MONTHS",
                    result_function=PostparsingValidators.isGreaterThan(0),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="OTHER_AMOUNT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="OTHER_NBR_MONTHS",
                    result_function=PostparsingValidators.isGreaterThan(0),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="WORK_REQ_SANCTION",
                    result_function=PostparsingValidators.isOneOf((1, 2)),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="FAMILY_SANC_ADULT",
                    result_function=PostparsingValidators.isOneOf((1, 2)),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="SANC_TEEN_PARENT",
                    result_function=PostparsingValidators.isOneOf((1, 2)),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="NON_COOPERATION_CSE",
                    result_function=PostparsingValidators.isOneOf((1, 2)),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="FAILURE_TO_COMPLY",
                    result_function=PostparsingValidators.isOneOf((1, 2)),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="SANC_REDUCTION_AMT",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="OTHER_SANCTION",
                    result_function=PostparsingValidators.isOneOf((1, 2)),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="OTHER_TOTAL_REDUCTIONS",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="FAMILY_CAP",
                    result_function=PostparsingValidators.isOneOf((1, 2)),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="OTHER_TOTAL_REDUCTIONS",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="REDUCTIONS_ON_RECEIPTS",
                    result_function=PostparsingValidators.isOneOf((1, 2)),
                ),
                PostparsingValidators.ifThenAlso(
                    condition_field_name="OTHER_TOTAL_REDUCTIONS",
                    condition_function=PostparsingValidators.isGreaterThan(0),
                    result_field_name="OTHER_NON_SANCTION",
                    result_function=PostparsingValidators.isOneOf((1, 2)),
                ),
                PostparsingValidators.sumIsLarger(
                    (
                        "AMT_FOOD_STAMP_ASSISTANCE",
                        "AMT_SUB_CC",
                        "CASH_AMOUNT",
                        "CC_AMOUNT",
                        "TRANSP_AMOUNT",
                        "TRANSITION_SERVICES_AMOUNT",
                        "OTHER_AMOUNT",
                    ),
                    0,
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
                    item="4",
                    name="RPT_MONTH_YEAR",
                    friendly_name="Reporting Year and Month",
                    type="number",
                    startIndex=2,
                    endIndex=8,
                    required=True,
                    validators=[
                        FieldValidators.dateYearIsLargerThan(1900),
                        FieldValidators.dateMonthIsValid(),
                    ],
                ),
                Field(
                    item="6",
                    name="CASE_NUMBER",
                    friendly_name="Case Number--TANF",
                    type="string",
                    startIndex=8,
                    endIndex=19,
                    required=True,
                    validators=[FieldValidators.isNotEmpty()],
                ),
                TransformField(
                    zero_pad(3),
                    item="2",
                    name="COUNTY_FIPS_CODE",
                    friendly_name="County FIPS Code",
                    type="string",
                    startIndex=19,
                    endIndex=22,
                    required=False,
                    validators=[FieldValidators.isNumber()],
                ),
                Field(
                    item="5",
                    name="STRATUM",
                    friendly_name="Stratum",
                    type="string",
                    startIndex=22,
                    endIndex=24,
                    required=False,
                    validators=[
                        FieldValidators.isBetween(0, 99, inclusive=True, cast=int),
                    ],
                ),
                Field(
                    item="7",
                    name="ZIP_CODE",
                    friendly_name="ZIP Code",
                    type="string",
                    startIndex=24,
                    endIndex=29,
                    required=True,
                    validators=[
                        FieldValidators.isNumber(),
                    ],
                ),
                Field(
                    item="8",
                    name="FUNDING_STREAM",
                    friendly_name="Funding Stream",
                    type="number",
                    startIndex=29,
                    endIndex=30,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(1, 2, inclusive=True),
                    ],
                ),
                Field(
                    item="9",
                    name="DISPOSITION",
                    friendly_name="Disposition",
                    type="number",
                    startIndex=30,
                    endIndex=31,
                    required=True,
                    validators=[
                        FieldValidators.isEqual(1),
                    ],
                ),
                Field(
                    item="10",
                    name="NEW_APPLICANT",
                    friendly_name="New Applicant",
                    type="number",
                    startIndex=31,
                    endIndex=32,
                    required=True,
                    validators=[
                        FieldValidators.isOneOf([1, 2]),
                    ],
                ),
                Field(
                    item="11",
                    name="NBR_FAMILY_MEMBERS",
                    friendly_name="Number of Family Members",
                    type="number",
                    startIndex=32,
                    endIndex=34,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(1, 99, inclusive=True),
                    ],
                ),
                Field(
                    item="12",
                    name="FAMILY_TYPE",
                    friendly_name="Type of Family for Work Participation",
                    type="number",
                    startIndex=34,
                    endIndex=35,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(1, 3, inclusive=True),
                    ],
                ),
                Field(
                    item="13",
                    name="RECEIVES_SUB_HOUSING",
                    friendly_name="Receives Subsidized Housing",
                    type="number",
                    startIndex=35,
                    endIndex=36,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(1, 3, inclusive=True),
                    ],
                ),
                Field(
                    item="14",
                    name="RECEIVES_MED_ASSISTANCE",
                    friendly_name="Receives Medical Assistance",
                    type="number",
                    startIndex=36,
                    endIndex=37,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(1, 2, inclusive=True),
                    ],
                ),
                Field(
                    item="15",
                    name="RECEIVES_FOOD_STAMPS",
                    friendly_name="Receives Food Stamps",
                    type="number",
                    startIndex=37,
                    endIndex=38,
                    required=False,
                    validators=[
                        FieldValidators.isBetween(0, 2, inclusive=True),
                    ],
                ),
                Field(
                    item="16",
                    name="AMT_FOOD_STAMP_ASSISTANCE",
                    friendly_name="Amount of Food Stamp Assistance",
                    type="number",
                    startIndex=38,
                    endIndex=42,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="17",
                    name="RECEIVES_SUB_CC",
                    friendly_name="Receives Subsidized Child Care",
                    type="number",
                    startIndex=42,
                    endIndex=43,
                    required=False,
                    validators=[
                        FieldValidators.isBetween(0, 3, inclusive=True),
                    ],
                ),
                Field(
                    item="18",
                    name="AMT_SUB_CC",
                    friendly_name="Amount of Subsidized Child Care",
                    type="number",
                    startIndex=43,
                    endIndex=47,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="19",
                    name="CHILD_SUPPORT_AMT",
                    friendly_name="Amount of Child Support",
                    type="number",
                    startIndex=47,
                    endIndex=51,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="20",
                    name="FAMILY_CASH_RESOURCES",
                    friendly_name="Amount of the Family's Cash Resources",
                    type="number",
                    startIndex=51,
                    endIndex=55,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="21A",
                    name="CASH_AMOUNT",
                    friendly_name="Cash Amount",
                    type="number",
                    startIndex=55,
                    endIndex=59,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="21B",
                    name="NBR_MONTHS",
                    friendly_name="Number of Months",
                    type="number",
                    startIndex=59,
                    endIndex=62,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 999, inclusive=True),
                    ],
                ),
                Field(
                    item="22A",
                    name="CC_AMOUNT",
                    friendly_name="TANF Child Care Care Amount",
                    type="number",
                    startIndex=62,
                    endIndex=66,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="22B",
                    name="CHILDREN_COVERED",
                    friendly_name="TANF Child Care Number of Children Covered",
                    type="number",
                    startIndex=66,
                    endIndex=68,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 99, inclusive=True),
                    ],
                ),
                Field(
                    item="22C",
                    name="CC_NBR_MONTHS",
                    friendly_name="TANF Child Care Number of Months",
                    type="number",
                    startIndex=68,
                    endIndex=71,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 999, inclusive=True),
                    ],
                ),
                Field(
                    item="23A",
                    name="TRANSP_AMOUNT",
                    friendly_name="Transportation Amount",
                    type="number",
                    startIndex=71,
                    endIndex=75,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="23B",
                    name="TRANSP_NBR_MONTHS",
                    friendly_name="Transportation Number of Months",
                    type="number",
                    startIndex=75,
                    endIndex=78,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 999, inclusive=True),
                    ],
                ),
                Field(
                    item="24A",
                    name="TRANSITION_SERVICES_AMOUNT",
                    friendly_name="Transitional Services Amount",
                    type="number",
                    startIndex=78,
                    endIndex=82,
                    required=False,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="24B",
                    name="TRANSITION_NBR_MONTHS",
                    friendly_name="Transitional Services Number of Months",
                    type="number",
                    startIndex=82,
                    endIndex=85,
                    required=False,
                    validators=[
                        FieldValidators.isBetween(0, 999, inclusive=True),
                    ],
                ),
                Field(
                    item="25A",
                    name="OTHER_AMOUNT",
                    friendly_name="Other Amount",
                    type="number",
                    startIndex=85,
                    endIndex=89,
                    required=False,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="25B",
                    name="OTHER_NBR_MONTHS",
                    friendly_name="Other Number of Months",
                    type="number",
                    startIndex=89,
                    endIndex=92,
                    required=False,
                    validators=[
                        FieldValidators.isBetween(0, 999, inclusive=True),
                    ],
                ),
                Field(
                    item="26AI",
                    name="SANC_REDUCTION_AMT",
                    friendly_name="Total Dollar Amount of Reductions due to Sanctions",
                    type="number",
                    startIndex=92,
                    endIndex=96,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="26AII",
                    name="WORK_REQ_SANCTION",
                    friendly_name="Work Requirements Sanction",
                    type="number",
                    startIndex=96,
                    endIndex=97,
                    required=True,
                    validators=[
                        FieldValidators.isOneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26AIII",
                    name="FAMILY_SANC_ADULT",
                    friendly_name="Family Sanction for an Adult with No High School Diploma or Equivalent:",
                    type="number",
                    startIndex=97,
                    endIndex=98,
                    required=False,
                    validators=[
                        FieldValidators.isOneOf([0, 1, 2]),
                    ],
                ),
                Field(
                    item="26AIV",
                    name="SANC_TEEN_PARENT",
                    friendly_name="Sanction for Teen Parent not Attending School",
                    type="number",
                    startIndex=98,
                    endIndex=99,
                    required=True,
                    validators=[
                        FieldValidators.isOneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26AV",
                    name="NON_COOPERATION_CSE",
                    friendly_name="Non-Cooperation with Child Support",
                    type="number",
                    startIndex=99,
                    endIndex=100,
                    required=True,
                    validators=[
                        FieldValidators.isOneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26AVI",
                    name="FAILURE_TO_COMPLY",
                    friendly_name="Failure to comply with an Individual Responsibility Plan",
                    type="number",
                    startIndex=100,
                    endIndex=101,
                    required=True,
                    validators=[
                        FieldValidators.isOneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26AVII",
                    name="OTHER_SANCTION",
                    friendly_name="Other Sanction",
                    type="number",
                    startIndex=101,
                    endIndex=102,
                    required=True,
                    validators=[
                        FieldValidators.isOneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26B",
                    name="RECOUPMENT_PRIOR_OVRPMT",
                    friendly_name="Recoupment of Prior Overpayment",
                    type="number",
                    startIndex=102,
                    endIndex=106,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="26CI",
                    name="OTHER_TOTAL_REDUCTIONS",
                    friendly_name="Total Dollar Amount of Reductions due to Other Reasons",
                    type="number",
                    startIndex=106,
                    endIndex=110,
                    required=True,
                    validators=[
                        FieldValidators.isBetween(0, 9999, inclusive=True),
                    ],
                ),
                Field(
                    item="26CII",
                    name="FAMILY_CAP",
                    friendly_name="Family Cap",
                    type="number",
                    startIndex=110,
                    endIndex=111,
                    required=True,
                    validators=[
                        FieldValidators.isOneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26CIII",
                    name="REDUCTIONS_ON_RECEIPTS",
                    friendly_name="Reduction Based on Length of Receipt of Assistance",
                    type="number",
                    startIndex=111,
                    endIndex=112,
                    required=True,
                    validators=[
                        FieldValidators.isOneOf([1, 2]),
                    ],
                ),
                Field(
                    item="26CIV",
                    name="OTHER_NON_SANCTION",
                    friendly_name="Other, Non-sanction",
                    type="number",
                    startIndex=112,
                    endIndex=113,
                    required=True,
                    validators=[
                        FieldValidators.isOneOf([1, 2]),
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
                    validators=[FieldValidators.isBetween(0, 9, inclusive=True, cast=int)],
                ),
                Field(
                    item="28",
                    name="FAMILY_EXEMPT_TIME_LIMITS",
                    friendly_name="Exempt during reporting month from the Tribal Time-Limit Provisions",
                    type="number",
                    startIndex=114,
                    endIndex=116,
                    required=True,
                    validators=[FieldValidators.isBetween(0, 9, inclusive=True)],
                ),
                Field(
                    item="29",
                    name="FAMILY_NEW_CHILD",
                    friendly_name="A New Child-Only Family",
                    type="number",
                    startIndex=116,
                    endIndex=117,
                    required=False,
                    validators=[
                        FieldValidators.isOneOf([0, 1, 2]),
                    ],
                ),
                Field(
                    item="-1",
                    name="BLANK",
                    friendly_name="blank",
                    type="string",
                    startIndex=117,
                    endIndex=123,
                    required=False,
                    validators=[],
                ),
            ],
        )
    ]
)
