"""Schema for Tribal TANF T2 row of all submission types."""


from tdpservice.parsers.transforms import tanf_ssn_decryption_func, zero_pad
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers import validators
from tdpservice.search_indexes.documents.tribal import Tribal_TANF_T2DataSubmissionDocument


t2 = SchemaManager(
    schemas=[
        RowSchema(
            record_type="T2",
            document=Tribal_TANF_T2DataSubmissionDocument(),
            preparsing_validators=[
                validators.recordHasLength(122),
                validators.caseNumberNotEmpty(8, 19),
                validators.or_priority_validators([
                    validators.field_year_month_with_header_year_quarter(),
                    validators.validateRptMonthYear(),
                ]),
            ],
            postparsing_validators=[
                validators.validate__FAM_AFF__SSN(),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.matches(1),
                    result_field_name="SSN",
                    result_function=validators.validateSSN(),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="RACE_HISPANIC",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="RACE_AMER_INDIAN",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="RACE_ASIAN",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="RACE_BLACK",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="RACE_HAWAIIAN",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="RACE_WHITE",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="MARITAL_STATUS",
                    result_function=validators.isInLimits(1, 5),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 2),
                    result_field_name="PARENT_MINOR_CHILD",
                    result_function=validators.isInLimits(1, 3),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="EDUCATION_LEVEL",
                    result_function=validators.or_validators(
                        validators.isInStringRange(0, 16),
                        validators.isInStringRange(98, 99),
                    ),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.matches(1),
                    result_field_name="CITIZENSHIP_STATUS",
                    result_function=validators.matches(1),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="COOPERATION_CHILD_SUPPORT",
                    result_function=validators.oneOf((1, 2, 9)),
                ),
                validators.validate__FAM_AFF__HOH__Fed_Time(),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name="EMPLOYMENT_STATUS",
                    result_function=validators.isInLimits(1, 3),
                ),
                validators.if_then_validator(
                    condition_field_name="FAMILY_AFFILIATION",
                    condition_function=validators.oneOf((1, 2)),
                    result_field_name="WORK_PART_STATUS",
                    result_function=validators.or_validators(
                        validators.isInStringRange(1, 3),
                        validators.isInStringRange(5, 9),
                        validators.isInStringRange(11, 19),
                        validators.matches("99"),
                    ),
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
                        validators.dateYearIsLargerThan(1900),
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
                    item="30",
                    name="FAMILY_AFFILIATION",
                    friendly_name="family affiliation",
                    type="number",
                    startIndex=19,
                    endIndex=20,
                    required=True,
                    validators=[validators.oneOf([1, 2, 3, 5])],
                ),
                Field(
                    item="31",
                    name="NONCUSTODIAL_PARENT",
                    friendly_name="noncustodial parent",
                    type="number",
                    startIndex=20,
                    endIndex=21,
                    required=True,
                    validators=[validators.oneOf([1, 2])],
                ),
                Field(
                    item="32",
                    name="DATE_OF_BIRTH",
                    friendly_name="date of birth",
                    type="string",
                    startIndex=21,
                    endIndex=29,
                    required=True,
                    validators=[validators.intHasLength(8),
                                validators.dateYearIsLargerThan(1900),
                                validators.dateMonthIsValid(),
                                validators.dateDayIsValid()
                                ]
                ),
                TransformField(
                    transform_func=tanf_ssn_decryption_func,
                    item="33",
                    name="SSN",
                    friendly_name="social security number - ssn",
                    type="string",
                    startIndex=29,
                    endIndex=38,
                    required=True,
                    validators=[validators.isNumber()],
                    is_encrypted=False,
                ),
                Field(
                    item="34A",
                    name="RACE_HISPANIC",
                    friendly_name="race hispanic",
                    type="number",
                    startIndex=38,
                    endIndex=39,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="34B",
                    name="RACE_AMER_INDIAN",
                    friendly_name="race american-indian",
                    type="number",
                    startIndex=39,
                    endIndex=40,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="34C",
                    name="RACE_ASIAN",
                    friendly_name="race asian",
                    type="number",
                    startIndex=40,
                    endIndex=41,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="34D",
                    name="RACE_BLACK",
                    friendly_name="race black",
                    type="number",
                    startIndex=41,
                    endIndex=42,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="34E",
                    name="RACE_HAWAIIAN",
                    friendly_name="race hawaiian",
                    type="number",
                    startIndex=42,
                    endIndex=43,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="34F",
                    name="RACE_WHITE",
                    friendly_name="race white",
                    type="number",
                    startIndex=43,
                    endIndex=44,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="35",
                    name="GENDER",
                    friendly_name="gender",
                    type="number",
                    startIndex=44,
                    endIndex=45,
                    required=False,
                    validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ],
                ),
                Field(
                    item="36A",
                    name="FED_OASDI_PROGRAM",
                    friendly_name="federal old age survivors and disability insurance program",
                    type="number",
                    startIndex=45,
                    endIndex=46,
                    required=True,
                    validators=[validators.oneOf([1, 2])],
                ),
                Field(
                    item="36B",
                    name="FED_DISABILITY_STATUS",
                    friendly_name="federal disability status",
                    type="number",
                    startIndex=46,
                    endIndex=47,
                    required=True,
                    validators=[validators.oneOf([1, 2])],
                ),
                Field(
                    item="36C",
                    name="DISABLED_TITLE_XIVAPDT",
                    friendly_name="Receives Aid to the Permanently and Totally Disabled" +
                    " Under Title XIV-APDT of the Social Security Act",
                    type="string",
                    startIndex=47,
                    endIndex=48,
                    required=True,
                    validators=[
                        validators.or_validators(
                            validators.oneOf(["1", "2"]), validators.isBlank()
                        )
                    ],
                ),
                Field(
                    item="36D",
                    name="AID_AGED_BLIND",
                    friendly_name="receives from the aid to the aged, blind, and disabled program",
                    type="number",
                    startIndex=48,
                    endIndex=49,
                    required=False,
                    validators=[
                        validators.isInLimits(0, 2),
                    ],
                ),
                Field(
                    item="36E",
                    name="RECEIVE_SSI",
                    friendly_name="receives social security income",
                    type="number",
                    startIndex=49,
                    endIndex=50,
                    required=True,
                    validators=[
                        validators.oneOf([1, 2]),
                    ],
                ),
                Field(
                    item="37",
                    name="MARITAL_STATUS",
                    friendly_name="marital status",
                    type="number",
                    startIndex=50,
                    endIndex=51,
                    required=False,
                    validators=[
                        validators.isInLimits(0, 5),
                    ],
                ),
                Field(
                    item="38",
                    name="RELATIONSHIP_HOH",
                    friendly_name="relationship to head of household",
                    type="string",
                    startIndex=51,
                    endIndex=53,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 10),
                    ],
                ),
                Field(
                    item="39",
                    name="PARENT_MINOR_CHILD",
                    friendly_name="parent of minor child",
                    type="number",
                    startIndex=53,
                    endIndex=54,
                    required=False,
                    validators=[
                        validators.isInLimits(0, 3),
                    ],
                ),
                Field(
                    item="40",
                    name="NEEDS_PREGNANT_WOMAN",
                    friendly_name="needs of pregnant woman",
                    type="number",
                    startIndex=54,
                    endIndex=55,
                    required=False,
                    validators=[
                        validators.isInLimits(0, 2),
                    ],
                ),
                Field(
                    item="41",
                    name="EDUCATION_LEVEL",
                    friendly_name="education level",
                    type="string",
                    startIndex=55,
                    endIndex=57,
                    required=False,
                    validators=[
                        validators.or_validators(
                            validators.isInStringRange(0, 16),
                            validators.isInStringRange(98, 99),
                        )
                    ],
                ),
                Field(
                    item="42",
                    name="CITIZENSHIP_STATUS",
                    friendly_name="citizenship status",
                    type="number",
                    startIndex=57,
                    endIndex=58,
                    required=False,
                    validators=[validators.oneOf([0, 1, 2, 9])],
                ),
                Field(
                    item="43",
                    name="COOPERATION_CHILD_SUPPORT",
                    friendly_name="cooperation with child support",
                    type="number",
                    startIndex=58,
                    endIndex=59,
                    required=False,
                    validators=[
                        validators.oneOf([0, 1, 2, 9]),
                    ],
                ),
                Field(
                    item="44",
                    name="MONTHS_FED_TIME_LIMIT",
                    friendly_name="countable months toward federal time limit",
                    type="string",
                    startIndex=59,
                    endIndex=62,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 999),
                    ],
                ),
                Field(
                    item="45",
                    name="MONTHS_STATE_TIME_LIMIT",
                    friendly_name="months of state time limit",
                    type="string",
                    startIndex=62,
                    endIndex=64,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="46",
                    name="CURRENT_MONTH_STATE_EXEMPT",
                    friendly_name="current month state exempt",
                    type="number",
                    startIndex=64,
                    endIndex=65,
                    required=False,
                    validators=[
                        validators.isInLimits(0, 2),
                    ],
                ),
                Field(
                    item="47",
                    name="EMPLOYMENT_STATUS",
                    friendly_name="employment status",
                    type="number",
                    startIndex=65,
                    endIndex=66,
                    required=False,
                    validators=[
                        validators.isInLimits(0, 3),
                    ],
                ),
                Field(
                    item="48",
                    name="WORK_PART_STATUS",
                    friendly_name="work participation status",
                    type="string",
                    startIndex=66,
                    endIndex=68,
                    required=False,
                    validators=[
                        validators.or_validators(
                            validators.isInStringRange(0, 3),
                            validators.isInStringRange(5, 9),
                            validators.isInStringRange(11, 19),
                            validators.matches("99"),
                        )
                    ],
                ),
                Field(
                    item="49",
                    name="UNSUB_EMPLOYMENT",
                    friendly_name="unsubsidized employment",
                    type="string",
                    startIndex=68,
                    endIndex=70,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="50",
                    name="SUB_PRIVATE_EMPLOYMENT",
                    friendly_name="subsidized private employment",
                    type="string",
                    startIndex=70,
                    endIndex=72,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="51",
                    name="SUB_PUBLIC_EMPLOYMENT",
                    friendly_name="subsidized public employment",
                    type="string",
                    startIndex=72,
                    endIndex=74,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="52",
                    name="WORK_EXPERIENCE",
                    friendly_name="work experience",
                    type="string",
                    startIndex=74,
                    endIndex=76,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="53",
                    name="OJT",
                    friendly_name="on the job training",
                    type="string",
                    startIndex=76,
                    endIndex=78,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="54",
                    name="JOB_SEARCH",
                    friendly_name="job search",
                    type="string",
                    startIndex=78,
                    endIndex=80,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="55",
                    name="COMM_SERVICES",
                    friendly_name="community service",
                    type="string",
                    startIndex=80,
                    endIndex=82,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="56",
                    name="VOCATIONAL_ED_TRAINING",
                    friendly_name="vocational education",
                    type="string",
                    startIndex=82,
                    endIndex=84,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="57",
                    name="JOB_SKILLS_TRAINING",
                    friendly_name="job skills training",
                    type="string",
                    startIndex=84,
                    endIndex=86,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="58",
                    name="ED_NO_HIGH_SCHOOL_DIPLOMA",
                    friendly_name="education no high school diploma",
                    type="string",
                    startIndex=86,
                    endIndex=88,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="59",
                    name="SCHOOL_ATTENDENCE",
                    friendly_name="school attendance",
                    type="string",
                    startIndex=88,
                    endIndex=90,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="60",
                    name="PROVIDE_CC",
                    friendly_name="provide child care",
                    type="string",
                    startIndex=90,
                    endIndex=92,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                TransformField(
                    zero_pad(2),
                    item="61",
                    name="ADD_WORK_ACTIVITIES",
                    friendly_name="additional work activities",
                    type="string",
                    startIndex=92,
                    endIndex=94,
                    required=False,
                    validators=[
                        validators.matches("00"),
                    ],
                ),
                Field(
                    item="62",
                    name="OTHER_WORK_ACTIVITIES",
                    friendly_name="other work activities",
                    type="string",
                    startIndex=94,
                    endIndex=96,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="63",
                    name="REQ_HRS_WAIVER_DEMO",
                    friendly_name="required hours under waiver demo",
                    type="string",
                    startIndex=96,
                    endIndex=98,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 99),
                    ],
                ),
                Field(
                    item="64",
                    name="EARNED_INCOME",
                    friendly_name="earned income",
                    type="string",
                    startIndex=98,
                    endIndex=102,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 9999),
                    ],
                ),
                Field(
                    item="65A",
                    name="UNEARNED_INCOME_TAX_CREDIT",
                    friendly_name="unearned income tax credit",
                    type="string",
                    startIndex=102,
                    endIndex=106,
                    required=False,
                    validators=[
                        validators.isInStringRange(0, 9999),
                    ],
                ),
                Field(
                    item="65B",
                    name="UNEARNED_SOCIAL_SECURITY",
                    friendly_name="unearned social security",
                    type="string",
                    startIndex=106,
                    endIndex=110,
                    required=True,
                    validators=[
                        validators.isInStringRange(0, 9999),
                    ],
                ),
                Field(
                    item="65C",
                    name="UNEARNED_SSI",
                    friendly_name="unearned ssi benefit",
                    type="string",
                    startIndex=110,
                    endIndex=114,
                    required=True,
                    validators=[
                        validators.isInStringRange(0, 9999),
                    ],
                ),
                Field(
                    item="65D",
                    name="UNEARNED_WORKERS_COMP",
                    friendly_name="unearned workers compensation",
                    type="string",
                    startIndex=114,
                    endIndex=118,
                    required=True,
                    validators=[
                        validators.isInStringRange(0, 9999),
                    ],
                ),
                Field(
                    item="65E",
                    name="OTHER_UNEARNED_INCOME",
                    friendly_name="other unearned income",
                    type="string",
                    startIndex=118,
                    endIndex=122,
                    required=True,
                    validators=[
                        validators.isInStringRange(0, 9999),
                    ],
                ),
                Field(
                    item="-1",
                    name="BLANK",
                    friendly_name="blank",
                    type="string",
                    startIndex=122,
                    endIndex=123,
                    required=False,
                    validators=[],
                ),
            ],
        )
    ]
)
