"""Schema for Tribal TANF T3 row of all submission types."""


from ...transforms import tanf_ssn_decryption_func
from ...fields import TransformField, Field
from ...row_schema import RowSchema, SchemaManager
from ... import validators
from tdpservice.search_indexes.documents.tribal import Tribal_TANF_T3DataSubmissionDocument


child_one = RowSchema(
    record_type="T3",
    document=Tribal_TANF_T3DataSubmissionDocument(),
    preparsing_validators=[
        validators.notEmpty(start=19, end=60),
        validators.caseNumberNotEmpty(8, 19),
        validators.or_priority_validators([
                    validators.field_year_month_with_header_year_quarter(),
                    validators.validateRptMonthYear(),
                ]),
    ],
    postparsing_validators=[
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field_name="SSN",
            result_function=validators.validateSSN(),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_HISPANIC",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_AMER_INDIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_ASIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_BLACK",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_HAWAIIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_WHITE",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RELATIONSHIP_HOH",
            result_function=validators.isInStringRange(4, 9),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="PARENT_MINOR_CHILD",
            result_function=validators.oneOf((2, 3)),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field_name="EDUCATION_LEVEL",
            result_function=validators.notMatches("99"),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field_name="CITIZENSHIP_STATUS",
            result_function=validators.oneOf((1, 2)),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.matches(2),
            result_field_name="CITIZENSHIP_STATUS",
            result_function=validators.oneOf((1, 2, 9)),
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
            validators=[],
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
            item="66",
            name="FAMILY_AFFILIATION",
            friendly_name="family affiliation",
            type="number",
            startIndex=19,
            endIndex=20,
            required=True,
            validators=[validators.oneOf([1, 2, 4])],
        ),
        Field(
            item="67",
            name="DATE_OF_BIRTH",
            friendly_name="date of birth",
            type="string",
            startIndex=20,
            endIndex=28,
            required=True,
            validators=[validators.intHasLength(8),
                        validators.dateYearIsLargerThan(1900),
                        validators.dateMonthIsValid(),
                        validators.dateDayIsValid()
                        ]
        ),
        TransformField(
            transform_func=tanf_ssn_decryption_func,
            item="68",
            name="SSN",
            friendly_name="social security number - ssn",
            type="string",
            startIndex=28,
            endIndex=37,
            required=True,
            validators=[validators.isNumber()],
            is_encrypted=False,
        ),
        Field(
            item="69A",
            name="RACE_HISPANIC",
            friendly_name="race hispanic",
            type="number",
            startIndex=37,
            endIndex=38,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69B",
            name="RACE_AMER_INDIAN",
            friendly_name="race american indian",
            type="number",
            startIndex=38,
            endIndex=39,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69C",
            name="RACE_ASIAN",
            friendly_name="race asian",
            type="number",
            startIndex=39,
            endIndex=40,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69D",
            name="RACE_BLACK",
            friendly_name="race black",
            type="number",
            startIndex=40,
            endIndex=41,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69E",
            name="RACE_HAWAIIAN",
            friendly_name="race hawaiian",
            type="number",
            startIndex=41,
            endIndex=42,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69F",
            name="RACE_WHITE",
            friendly_name="race white",
            type="number",
            startIndex=42,
            endIndex=43,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="70",
            name="GENDER",
            friendly_name="gender",
            type="number",
            startIndex=43,
            endIndex=44,
            required=False,
            validators=[validators.isInLimits(0, 9)],
        ),
        Field(
            item="71A",
            name="RECEIVE_NONSSA_BENEFITS",
            friendly_name="receives non-social security act benefits",
            type="number",
            startIndex=44,
            endIndex=45,
            required=True,
            validators=[validators.oneOf([1, 2])],
        ),
        Field(
            item="71B",
            name="RECEIVE_SSI",
            friendly_name="receives social security income",
            type="number",
            startIndex=45,
            endIndex=46,
            required=True,
            validators=[validators.oneOf([1, 2])],
        ),
        Field(
            item="72",
            name="RELATIONSHIP_HOH",
            friendly_name="relationship to head of household",
            type="string",
            startIndex=46,
            endIndex=48,
            required=False,
            validators=[validators.isInStringRange(0, 10)],
        ),
        Field(
            item="73",
            name="PARENT_MINOR_CHILD",
            friendly_name="parent of minor child",
            type="number",
            startIndex=48,
            endIndex=49,
            required=False,
            validators=[validators.oneOf([0, 2, 3])],
        ),
        Field(
            item="74",
            name="EDUCATION_LEVEL",
            friendly_name="education level",
            type="string",
            startIndex=49,
            endIndex=51,
            required=True,
            validators=[
                validators.or_validators(
                    validators.isInStringRange(0, 16),
                    validators.isInStringRange(98, 99),
                )
            ],
        ),
        Field(
            item="75",
            name="CITIZENSHIP_STATUS",
            friendly_name="citizenship status",
            type="number",
            startIndex=51,
            endIndex=52,
            required=False,
            validators=[validators.oneOf([0, 1, 2, 9])],
        ),
        Field(
            item="76A",
            name="UNEARNED_SSI",
            friendly_name="unearned ssi benefit",
            type="string",
            startIndex=52,
            endIndex=56,
            required=True,
            validators=[validators.isInStringRange(0, 9999)],
        ),
        Field(
            item="76B",
            name="OTHER_UNEARNED_INCOME",
            friendly_name="other unearned income",
            type="string",
            startIndex=56,
            endIndex=60,
            required=True,
            validators=[validators.isInStringRange(0, 9999)],
        ),
    ],
)

child_two = RowSchema(
    record_type="T3",
    document=Tribal_TANF_T3DataSubmissionDocument(),
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(start=60, end=101),
        validators.caseNumberNotEmpty(8, 19),
        validators.or_priority_validators([
                    validators.field_year_month_with_header_year_quarter(),
                    validators.validateRptMonthYear(),
                ]),
    ],
    postparsing_validators=[
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field_name="SSN",
            result_function=validators.validateSSN(),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_HISPANIC",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_AMER_INDIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_ASIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_BLACK",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_HAWAIIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RACE_WHITE",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="RELATIONSHIP_HOH",
            result_function=validators.isInStringRange(4, 9),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field_name="PARENT_MINOR_CHILD",
            result_function=validators.oneOf((2, 3)),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field_name="EDUCATION_LEVEL",
            result_function=validators.notMatches("99"),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field_name="CITIZENSHIP_STATUS",
            result_function=validators.oneOf((1, 2)),
        ),
        validators.if_then_validator(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=validators.matches(2),
            result_field_name="CITIZENSHIP_STATUS",
            result_function=validators.oneOf((1, 2, 9)),
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
            validators=[],
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
            item="66",
            name="FAMILY_AFFILIATION",
            friendly_name="family affiliation",
            type="number",
            startIndex=60,
            endIndex=61,
            required=True,
            validators=[validators.oneOf([1, 2, 4])],
        ),
        Field(
            item="67",
            name="DATE_OF_BIRTH",
            friendly_name="date of birth",
            type="string",
            startIndex=61,
            endIndex=69,
            required=True,
            validators=[validators.intHasLength(8),
                        validators.dateYearIsLargerThan(1900),
                        validators.dateMonthIsValid(),
                        validators.dateDayIsValid()
                        ]
        ),
        TransformField(
            transform_func=tanf_ssn_decryption_func,
            item="68",
            name="SSN",
            friendly_name="social security number - ssn",
            type="string",
            startIndex=69,
            endIndex=78,
            required=True,
            validators=[validators.isNumber()],
            is_encrypted=False,
        ),
        Field(
            item="69A",
            name="RACE_HISPANIC",
            friendly_name="race hispanic",
            type="number",
            startIndex=78,
            endIndex=79,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69B",
            name="RACE_AMER_INDIAN",
            friendly_name="race american indian",
            type="number",
            startIndex=79,
            endIndex=80,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69C",
            name="RACE_ASIAN",
            friendly_name="race asian",
            type="number",
            startIndex=80,
            endIndex=81,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69D",
            name="RACE_BLACK",
            friendly_name="race black",
            type="number",
            startIndex=81,
            endIndex=82,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69E",
            name="RACE_HAWAIIAN",
            friendly_name="race hawaiian",
            type="number",
            startIndex=82,
            endIndex=83,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="69F",
            name="RACE_WHITE",
            friendly_name="race white",
            type="number",
            startIndex=83,
            endIndex=84,
            required=False,
            validators=[validators.validateRace()],
        ),
        Field(
            item="70",
            name="GENDER",
            friendly_name="gender",
            type="number",
            startIndex=84,
            endIndex=85,
            required=False,
            validators=[validators.isInLimits(0, 9)],
        ),
        Field(
            item="71A",
            name="RECEIVE_NONSSA_BENEFITS",
            friendly_name="receives non-ssa benefits",
            type="number",
            startIndex=85,
            endIndex=86,
            required=True,
            validators=[validators.oneOf([1, 2])],
        ),
        Field(
            item="71B",
            name="RECEIVE_SSI",
            friendly_name="receives SSI",
            type="number",
            startIndex=86,
            endIndex=87,
            required=True,
            validators=[validators.oneOf([1, 2])],
        ),
        Field(
            item="72",
            name="RELATIONSHIP_HOH",
            friendly_name="relationship to head of household",
            type="string",
            startIndex=87,
            endIndex=89,
            required=False,
            validators=[validators.isInStringRange(0, 10)],
        ),
        Field(
            item="73",
            name="PARENT_MINOR_CHILD",
            friendly_name="parent of minor child",
            type="number",
            startIndex=89,
            endIndex=90,
            required=False,
            validators=[validators.oneOf([0, 2, 3])],
        ),
        Field(
            item="74",
            name="EDUCATION_LEVEL",
            friendly_name="education level",
            type="string",
            startIndex=90,
            endIndex=92,
            required=True,
            validators=[
                validators.or_validators(
                    validators.isInStringRange(0, 16), validators.oneOf(["98", "99"])
                )
            ],
        ),
        Field(
            item="75",
            name="CITIZENSHIP_STATUS",
            friendly_name="citizenship status",
            type="number",
            startIndex=92,
            endIndex=93,
            required=False,
            validators=[validators.oneOf([0, 1, 2, 9])],
        ),
        Field(
            item="76A",
            name="UNEARNED_SSI",
            friendly_name="unearned ssi benefit",
            type="string",
            startIndex=93,
            endIndex=97,
            required=True,
            validators=[validators.isInStringRange(0, 9999)],
        ),
        Field(
            item="76B",
            name="OTHER_UNEARNED_INCOME",
            friendly_name="other unearned income",
            type="string",
            startIndex=97,
            endIndex=101,
            required=True,
            validators=[validators.isInStringRange(0, 9999)],
        ),
    ],
)

t3 = SchemaManager(schemas=[child_one, child_two])
