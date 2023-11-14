"""Schema for HEADER row of all submission types."""


from ...util import SchemaManager
from ...transforms import tanf_ssn_decryption_func
from ...fields import TransformField, Field
from ...row_schema import RowSchema
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T3


child_one = RowSchema(
    model=TANF_T3,
    preparsing_validators=[
        validators.notEmpty(start=19, end=60),
    ],
    postparsing_validators=[
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field="SSN",
            result_function=validators.validateSSN(),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_HISPANIC",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_AMER_INDIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_ASIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_BLACK",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_HAWAIIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_WHITE",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RELATIONSHIP_HOH",
            result_function=validators.isInStringRange(4, 9),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="PARENT_MINOR_CHILD",
            result_function=validators.oneOf((2, 3)),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field="EDUCATION_LEVEL",
            result_function=validators.notMatches("99"),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field="CITIZENSHIP_STATUS",
            result_function=validators.oneOf((1, 2)),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.matches(2),
            result_field="CITIZENSHIP_STATUS",
            result_function=validators.oneOf((1, 2, 9)),
        ),
    ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              friendly_name="record type", required=True, validators=[]),
        Field(item="4", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              friendly_name="report month year", required=True, validators=[]),
        Field(item="6", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              friendly_name="case number", required=True, validators=[validators.isAlphaNumeric()]),
        Field(item="67", name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
              friendly_name="family affiliation", required=True, validators=[
                  validators.oneOf([1, 2, 4])
              ]),
        Field(item="68", name='DATE_OF_BIRTH', type='number', startIndex=20, endIndex=28,
              friendly_name="date of birth", required=True, validators=[
                  validators.dateYearIsLargerThan(1998),
                  validators.dateMonthIsValid(),
              ]),
        TransformField(transform_func=tanf_ssn_decryption_func, item="69", name='SSN', type='string', startIndex=28,
                       endIndex=37, required=True,
                       friendly_name="social security name - ssn",
                       validators=[validators.validateSSN()],
                       is_encrypted=False),
        Field(item="70A", name='RACE_HISPANIC', type='number', startIndex=37, endIndex=38,
              friendly_name="race hispanic", required=False, validators=[validators.validateRace()]),
        Field(item="70B", name='RACE_AMER_INDIAN', type='number', startIndex=38, endIndex=39,
              friendly_name="race american indian", required=False, validators=[validators.validateRace()]),
        Field(item="70C", name='RACE_ASIAN', type='number', startIndex=39, endIndex=40,
              friendly_name="race asian", required=False, validators=[validators.validateRace()]),
        Field(item="70D", name='RACE_BLACK', type='number', startIndex=40, endIndex=41,
              friendly_name="race black", required=False, validators=[validators.validateRace()]),
        Field(item="70E", name='RACE_HAWAIIAN', type='number', startIndex=41, endIndex=42,
              friendly_name="race hawaiian", required=False, validators=[validators.validateRace()]),
        Field(item="70F", name='RACE_WHITE', type='number', startIndex=42, endIndex=43,
              friendly_name="race white", required=False, validators=[validators.validateRace()]),
        Field(item="71", name='GENDER', type='number', startIndex=43, endIndex=44,
              friendly_name="gender", required=True, validators=[
                  validators.isInLimits(0, 9)
              ]),
        Field(item="72A", name='RECEIVE_NONSSA_BENEFITS', type='number', startIndex=44, endIndex=45,
              friendly_name="receives nonssa benefits", required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="72B", name='RECEIVE_SSI', type='number', startIndex=45, endIndex=46,
              friendly_name="receive ssi", required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="73", name='RELATIONSHIP_HOH', type='string', startIndex=46, endIndex=48,
              friendly_name="relationship to head of household", required=False, validators=[
                  validators.isInStringRange(0, 10)
              ]),
        Field(item="74", name='PARENT_MINOR_CHILD', type='number', startIndex=48, endIndex=49,
              friendly_name="parent of minor child", required=False, validators=[
                  validators.oneOf([0, 2, 3])
              ]),
        Field(item="75", name='EDUCATION_LEVEL', type='string', startIndex=49, endIndex=51,
              friendly_name="education level", required=True, validators=[
                  validators.or_validators(
                      validators.isInStringRange(0, 16),
                      validators.isInStringRange(98, 99)
                  )
              ]),
        Field(item="76", name='CITIZENSHIP_STATUS', type='number', startIndex=51, endIndex=52,
              friendly_name="citizenship status", required=False, validators=[
                  validators.oneOf([0, 1, 2, 9])
              ]),
        Field(item="77A", name='UNEARNED_SSI', type='string', startIndex=52, endIndex=56,
              friendly_name="unearned ssi", required=False, validators=[
                  validators.isInStringRange(0, 9999)
              ]),
        Field(item="77B", name='OTHER_UNEARNED_INCOME', type='string', startIndex=56, endIndex=60,
              friendly_name="other unearned income", required=False, validators=[
                  validators.isInStringRange(0, 9999)
              ]),
    ],
)

child_two = RowSchema(
    model=TANF_T3,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(start=60, end=101),
    ],
    postparsing_validators=[
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field="SSN",
            result_function=validators.validateSSN(),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_HISPANIC",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_AMER_INDIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_ASIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_BLACK",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_HAWAIIAN",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RACE_WHITE",
            result_function=validators.isInLimits(1, 2),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="RELATIONSHIP_HOH",
            result_function=validators.isInStringRange(4, 9),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.oneOf((1, 2)),
            result_field="PARENT_MINOR_CHILD",
            result_function=validators.oneOf((2, 3)),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field="EDUCATION_LEVEL",
            result_function=validators.notMatches("99"),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.matches(1),
            result_field="CITIZENSHIP_STATUS",
            result_function=validators.oneOf((1, 2)),
        ),
        validators.if_then_validator(
            condition_field="FAMILY_AFFILIATION",
            condition_function=validators.matches(2),
            result_field="CITIZENSHIP_STATUS",
            result_function=validators.oneOf((1, 2, 9)),
        ),
    ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              friendly_name="record type", required=True, validators=[]),
        Field(item="4", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              friendly_name="report month year", required=True, validators=[]),
        Field(item="6", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              friendly_name="case number", required=True, validators=[validators.isAlphaNumeric()]),
        Field(item="67", name='FAMILY_AFFILIATION', type='number', startIndex=60, endIndex=61,
              friendly_name="family affiliation", required=True, validators=[
                  validators.oneOf([1, 2, 4])
              ]),
        Field(item="68", name='DATE_OF_BIRTH', type='number', startIndex=61, endIndex=69,
              friendly_name="date of birth", required=True, validators=[
                  validators.dateYearIsLargerThan(1998),
                  validators.dateMonthIsValid(),
              ]),
        TransformField(transform_func=tanf_ssn_decryption_func, item="69", name='SSN', type='string', startIndex=69,
                       friendly_name="social security number - SSN",
                       endIndex=78, required=True, validators=[validators.validateSSN()],
                       is_encrypted=False),
        Field(item="70A", name='RACE_HISPANIC', type='number', startIndex=78, endIndex=79,
              friendly_name="race hispanic", required=False, validators=[validators.validateRace()]),
        Field(item="70B", name='RACE_AMER_INDIAN', type='number', startIndex=79, endIndex=80,
              friendly_name="race american indian", required=False, validators=[validators.validateRace()]),
        Field(item="70C", name='RACE_ASIAN', type='number', startIndex=80, endIndex=81,
              friendly_name="race asian", required=False, validators=[validators.validateRace()]),
        Field(item="70D", name='RACE_BLACK', type='number', startIndex=81, endIndex=82,
              friendly_name="race black", required=False, validators=[validators.validateRace()]),
        Field(item="70E", name='RACE_HAWAIIAN', type='number', startIndex=82, endIndex=83,
              friendly_name="race hawaiian", required=False, validators=[validators.validateRace()]),
        Field(item="70F", name='RACE_WHITE', type='number', startIndex=83, endIndex=84,
              friendly_name="race white", required=False, validators=[validators.validateRace()]),
        Field(item="71", name='GENDER', type='number', startIndex=84, endIndex=85,
              friendly_name="gender", required=True, validators=[
                  validators.isInLimits(0, 9)
              ]),
        Field(item="72A", name='RECEIVE_NONSSA_BENEFITS', type='number', startIndex=85, endIndex=86,
              friendly_name="receive nonssa benefits", required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="72B", name='RECEIVE_SSI', type='number', startIndex=86, endIndex=87,
              friendly_name="receive ssi", required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="73", name='RELATIONSHIP_HOH', type='string', startIndex=87, endIndex=89,
              friendly_name="relationship head of household", required=False, validators=[
                  validators.isInStringRange(0, 10)
              ]),
        Field(item="74", name='PARENT_MINOR_CHILD', type='number', startIndex=89, endIndex=90,
              friendly_name="parent minor child", required=False, validators=[
                  validators.oneOf([0, 2, 3])
              ]),
        Field(item="75", name='EDUCATION_LEVEL', type='string', startIndex=90, endIndex=92,
              friendly_name="education level", required=True, validators=[
                  validators.or_validators(
                      validators.isInStringRange(0, 16),
                      validators.oneOf(['98', '99'])
                  )
              ]),
        Field(item="76", name='CITIZENSHIP_STATUS', type='number', startIndex=92, endIndex=93,
              friendly_name="citizenship status", required=False, validators=[
                  validators.oneOf([0, 1, 2, 9])
              ]),
        Field(item="77A", name='UNEARNED_SSI', type='string', startIndex=93, endIndex=97,
              friendly_name="unearned ssi", required=False, validators=[
                  validators.isInStringRange(0, 9999)
              ]),
        Field(item="77B", name='OTHER_UNEARNED_INCOME', type='string', startIndex=97, endIndex=101,
              friendly_name="other unearned income", required=False, validators=[
                  validators.isInStringRange(0, 9999)
              ]),
    ],
)

t3 = SchemaManager(schemas=[child_one, child_two])
