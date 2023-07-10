"""Schema for HEADER row of all submission types."""


from ...util import MultiRecordRowSchema, RowSchema, Field
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T3


child_one = RowSchema(
    model=TANF_T3,
    preparsing_validators=[
        validators.notEmpty(start=19, end=60),
    ],
    postparsing_validators=[
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_HISPANIC', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_AMER_INDIAN', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_ASIAN', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_BLACK', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_HAWAIIAN', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_WHITE', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RELATIONSHIP_HOH', result_function=validators.isInLimits(4, 9),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='PARENT_MINOR_CHILD', result_function=validators.oneOf(("1", "2", "3")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='EDUCATION_LEVEL', result_function=validators.notMatches("99"),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(2),
                  result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf(("1", "2", "9")),
            ),
        ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="4", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              required=True, validators=[]),
        Field(item="6", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              required=True, validators=[]),
        Field(item="67", name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
              required=True, validators=[]),
        Field(item="68", name='DATE_OF_BIRTH', type='number', startIndex=20, endIndex=28,
              required=True, validators=[]),
        Field(item="69", name='SSN', type='number', startIndex=28, endIndex=37,
              required=True, validators=[]),
        Field(item="70A", name='RACE_HISPANIC', type='string', startIndex=37, endIndex=38,
              required=True, validators=[]),
        Field(item="70B", name='RACE_AMER_INDIAN', type='string', startIndex=38, endIndex=39,
              required=True, validators=[]),
        Field(item="70C", name='RACE_ASIAN', type='string', startIndex=39, endIndex=40,
              required=True, validators=[]),
        Field(item="70D", name='RACE_BLACK', type='string', startIndex=40, endIndex=41,
              required=True, validators=[]),
        Field(item="70E", name='RACE_HAWAIIAN', type='string', startIndex=41, endIndex=42,
              required=True, validators=[]),
        Field(item="70F", name='RACE_WHITE', type='string', startIndex=42, endIndex=43,
              required=True, validators=[]),
        Field(item="71", name='GENDER', type='number', startIndex=43, endIndex=44,
              required=True, validators=[]),
        Field(item="72A", name='RECEIVE_NONSSA_BENEFITS', type='string', startIndex=44, endIndex=45,
              required=True, validators=[]),
        Field(item="72B", name='RECEIVE_SSI', type='string', startIndex=45, endIndex=46,
              required=True, validators=[]),
        Field(item="73", name='RELATIONSHIP_HOH', type='number', startIndex=46, endIndex=48,
              required=True, validators=[]),
        Field(item="74", name='PARENT_MINOR_CHILD', type='string', startIndex=48, endIndex=49,
              required=True, validators=[]),
        Field(item="75", name='EDUCATION_LEVEL', type='string', startIndex=49, endIndex=51,
              required=True, validators=[]),
        Field(item="76", name='CITIZENSHIP_STATUS', type='string', startIndex=51, endIndex=52,
              required=True, validators=[]),
        Field(item="77A", name='UNEARNED_SSI', type='string', startIndex=52, endIndex=56,
              required=False, validators=[]),
        Field(item="77B", name='OTHER_UNEARNED_INCOME', type='string', startIndex=56, endIndex=60,
              required=False, validators=[]),
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
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='SSN', result_function=validators.notOneOf(("000000000", "111111111", "222222222",
                                                                           "333333333", "444444444", "555555555",
                                                                           "666666666", "777777777", "888888888",
                                                                           "999999999")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_HISPANIC', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_AMER_INDIAN', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_ASIAN', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_BLACK', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_HAWAIIAN', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RACE_WHITE', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='RELATIONSHIP_HOH', result_function=validators.isInLimits(4, 9),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                  result_field='PARENT_MINOR_CHILD', result_function=validators.oneOf(("1", "2", "3")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='EDUCATION_LEVEL', result_function=validators.notMatches("99"),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf(("1", "2")),
            ),
        validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(2),
                  result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf(("1", "2", "9")),
            ),
        ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="4", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              required=True, validators=[]),
        Field(item="6", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              required=True, validators=[]),
        Field(item="67", name='FAMILY_AFFILIATION', type='number', startIndex=60, endIndex=61,
              required=True, validators=[
                  validators.oneOf([1, 2, 4])
              ]),
        Field(item="68", name='DATE_OF_BIRTH', type='number', startIndex=61, endIndex=69,
              required=True, validators=[
                  validators.month_year_yearIsLargerThan(1998),
                  validators.month_year_monthIsValid(),
              ]),
        Field(item="69", name='SSN', type='number', startIndex=69, endIndex=78,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item="70A", name='RACE_HISPANIC', type='number', startIndex=78, endIndex=79,
              required=True, validators=[
                  validators.oneOf([0, 1, 2])
              ]),
        Field(item="70B", name='RACE_AMER_INDIAN', type='number', startIndex=79, endIndex=80,
              required=True, validators=[
                  validators.oneOf([0, 1, 2])
              ]),
        Field(item="70C", name='RACE_ASIAN', type='number', startIndex=80, endIndex=81,
              required=True, validators=[
                  validators.oneOf([0, 1, 2])
              ]),
        Field(item="70D", name='RACE_BLACK', type='number', startIndex=81, endIndex=82,
              required=True, validators=[
                  validators.oneOf([0, 1, 2])
              ]),
        Field(item="70E", name='RACE_HAWAIIAN', type='number', startIndex=82, endIndex=83,
              required=True, validators=[
                  validators.oneOf([0, 1, 2])
              ]),
        Field(item="70F", name='RACE_WHITE', type='number', startIndex=83, endIndex=84,
              required=True, validators=[
                  validators.oneOf([0, 1, 2])
              ]),
        Field(item="71", name='GENDER', type='number', startIndex=84, endIndex=85,
              required=True, validators=[
                  validators.isInLimits(0, 9)
              ]),
        Field(item="72A", name='RECEIVE_NONSSA_BENEFITS', type='nummber', startIndex=85, endIndex=86,
              required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="72B", name='RECEIVE_SSI', type='number', startIndex=86, endIndex=87,
              required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="73", name='RELATIONSHIP_HOH', type='number', startIndex=87, endIndex=89,
              required=True, validators=[
                  validators.isInLimits(0, 10)
              ]),
        Field(item="74", name='PARENT_MINOR_CHILD', type='number', startIndex=89, endIndex=90,
              required=True, validators=[
                  validators.oneOf([0, 2, 3])
              ]),
        Field(item="75", name='EDUCATION_LEVEL', type='number', startIndex=90, endIndex=92,
              required=True, validators=[
                  validators.or_validators(
                      validators.isInLimits(0, 16),
                      validators.oneOf([98, 99])
                  )
              ]),
        Field(item="76", name='CITIZENSHIP_STATUS', type='number', startIndex=92, endIndex=93,
              required=True, validators=[
                  validators.oneOf([0, 1, 2, 9])
              ]),
        Field(item="77A", name='UNEARNED_SSI', type='number', startIndex=93, endIndex=97,
              required=False, validators=[
                  validators.isLargerThanOrEqualTo(0)
              ]),
        Field(item="77B", name='OTHER_UNEARNED_INCOME', type='number', startIndex=97, endIndex=101,
              required=False, validators=[
                  validators.isLargerThanOrEqualTo(0)
              ]),
    ],
)

t3 = MultiRecordRowSchema(
    schemas=[
        child_one,
        child_two
    ]
)
