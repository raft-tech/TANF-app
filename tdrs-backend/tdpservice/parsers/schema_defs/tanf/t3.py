"""Schema for HEADER row of all submission types."""


from ..cat3_validators import cat3_validate_t3
from ...util import MultiRecordRowSchema, RowSchema, Field
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T3


child_one = RowSchema(
    model=TANF_T3,
    preparsing_validators=[
        validators.notEmpty(start=19, end=60),
    ],
    postparsing_validators=[cat3_validate_t3,],
    fields=[
        Field(item=1, name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item=2, name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              required=True, validators=[]),
        Field(item=3, name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              required=True, validators=[]),
        Field(item=4, name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
              required=True, validators=[]),
        Field(item=5, name='DATE_OF_BIRTH', type='number', startIndex=20, endIndex=28,
              required=True, validators=[]),
        Field(item=6, name='SSN', type='string', startIndex=28, endIndex=37,
              required=True, validators=[]),
        Field(item=7, name='RACE_HISPANIC', type='string', startIndex=37, endIndex=38,
              required=True, validators=[]),
        Field(item=8, name='RACE_AMER_INDIAN', type='string', startIndex=38, endIndex=39,
              required=True, validators=[]),
        Field(item=9, name='RACE_ASIAN', type='string', startIndex=39, endIndex=40,
              required=True, validators=[]),
        Field(item=10, name='RACE_BLACK', type='string', startIndex=40, endIndex=41,
              required=True, validators=[]),
        Field(item=11, name='RACE_HAWAIIAN', type='string', startIndex=41, endIndex=42,
              required=True, validators=[]),
        Field(item=12, name='RACE_WHITE', type='string', startIndex=42, endIndex=43,
              required=True, validators=[]),
        Field(item=13, name='GENDER', type='number', startIndex=43, endIndex=44,
              required=True, validators=[]),
        Field(item=14, name='RECEIVE_NONSSA_BENEFITS', type='string', startIndex=44, endIndex=45,
              required=True, validators=[]),
        Field(item=15, name='RECEIVE_SSI', type='string', startIndex=45, endIndex=46,
              required=True, validators=[]),
        Field(item=16, name='RELATIONSHIP_HOH', type='number', startIndex=46, endIndex=48,
              required=True, validators=[]),
        Field(item=17, name='PARENT_MINOR_CHILD', type='string', startIndex=48, endIndex=49,
              required=True, validators=[]),
        Field(item=18, name='EDUCATION_LEVEL', type='string', startIndex=49, endIndex=51,
              required=True, validators=[]),
        Field(item=19, name='CITIZENSHIP_STATUS', type='string', startIndex=51, endIndex=52,
              required=True, validators=[]),
        Field(item=20, name='UNEARNED_SSI', type='string', startIndex=52, endIndex=56,
              required=False, validators=[]),
        Field(item=21, name='OTHER_UNEARNED_INCOME', type='string', startIndex=56, endIndex=60,
              required=False, validators=[]),
    ],
)

child_two = RowSchema(
    model=TANF_T3,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(start=60, end=101),
    ],
    postparsing_validators=[],
    fields=[
        Field(item=1, name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item=2, name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              required=True, validators=[]),
        Field(item=3, name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              required=True, validators=[]),
        Field(item=22, name='FAMILY_AFFILIATION', type='number', startIndex=60, endIndex=61,
              required=True, validators=[]),
        Field(item=23, name='DATE_OF_BIRTH', type='number', startIndex=61, endIndex=69,
              required=True, validators=[]),
        Field(item=24, name='SSN', type='string', startIndex=69, endIndex=78,
              required=True, validators=[]),
        Field(item=25, name='RACE_HISPANIC', type='string', startIndex=78, endIndex=79,
              required=True, validators=[]),
        Field(item=26, name='RACE_AMER_INDIAN', type='string', startIndex=79, endIndex=80,
              required=True, validators=[]),
        Field(item=27, name='RACE_ASIAN', type='string', startIndex=80, endIndex=81,
              required=True, validators=[]),
        Field(item=28, name='RACE_BLACK', type='string', startIndex=81, endIndex=82,
              required=True, validators=[]),
        Field(item=29, name='RACE_HAWAIIAN', type='string', startIndex=82, endIndex=83,
              required=True, validators=[]),
        Field(item=30, name='RACE_WHITE', type='string', startIndex=83, endIndex=84,
              required=True, validators=[]),
        Field(item=31, name='GENDER', type='number', startIndex=84, endIndex=85,
              required=True, validators=[]),
        Field(item=32, name='RECEIVE_NONSSA_BENEFITS', type='string', startIndex=85, endIndex=86,
              required=True, validators=[]),
        Field(item=33, name='RECEIVE_SSI', type='string', startIndex=86, endIndex=87,
              required=True, validators=[]),
        Field(item=34, name='RELATIONSHIP_HOH', type='number', startIndex=87, endIndex=89,
              required=True, validators=[]),
        Field(item=35, name='PARENT_MINOR_CHILD', type='string', startIndex=89, endIndex=90,
              required=True, validators=[]),
        Field(item=36, name='EDUCATION_LEVEL', type='string', startIndex=90, endIndex=92,
              required=True, validators=[]),
        Field(item=37, name='CITIZENSHIP_STATUS', type='string', startIndex=92, endIndex=93,
              required=True, validators=[]),
        Field(item=38, name='UNEARNED_SSI', type='string', startIndex=93, endIndex=97,
              required=False, validators=[]),
        Field(item=39, name='OTHER_UNEARNED_INCOME', type='string', startIndex=97, endIndex=101,
              required=False, validators=[]),
    ],
)

t3 = MultiRecordRowSchema(
    schemas=[
        child_one,
        child_two
    ]
)
