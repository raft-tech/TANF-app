"""Schema for HEADER row of all submission types."""


from ...util import MultiRecordRowSchema, RowSchema, Field
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T3


child_one= RowSchema(
    model=TANF_T3,
    preparsing_validators=[
        validators.notEmpty(start=19, end=60),
    ],
    postparsing_validators=[],
    fields=[
        Field(name='RecordType', type='string', startIndex=0, endIndex=2, required=True, validators=[
        ]),
        Field(name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8, required=True, validators=[
        ]),
        Field(name='CASE_NUMBER', type='string', startIndex=8, endIndex=19, required=True, validators=[
        ]),
        Field(name='FAMILY_AFFILIATION', type='string', startIndex=19, endIndex=20, required=True, validators=[
        ]),
        Field(name='DOB', type='number', startIndex=20, endIndex=28, required=True, validators=[
        ]),
        Field(name='SSN', type='string', startIndex=28, endIndex=37, required=True, validators=[
        ]),
        Field(name='ITEM70A_HISPANIC_OR_LATINO', type='string', startIndex=37, endIndex=38, required=True, validators=[
        ]),
        Field(name='ITEM70B_AMERICAN_INDIAN_OR_ALASKA_NATIVE', type='string', startIndex=38, endIndex=39, required=True,
              validators=[]),
        Field(name='ITEM70C_ASIAN', type='string', startIndex=39, endIndex=40, required=True, validators=[
        ]),
        Field(name='ITEM70D_BLACK_OR_AFRICAN_AMERICAN', type='string', startIndex=40, endIndex=41, required=True,
              validators=[]),
        Field(name='ITEM70E_NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER', type='string', startIndex=41, endIndex=42,
              required=True, validators=[]),
        Field(name='ITEM70F_WHITE', type='string', startIndex=42, endIndex=43, required=True, validators=[
        ]),
        Field(name='GENDER', type='string', startIndex=43, endIndex=44, required=True, validators=[
        ]),
        Field(name='ITEM72A_RECEIVES_BENEFITS_UNDER_NON_SSA_PROGRAMS', type='string',
              startIndex=44, endIndex=45, required=True, validators=[]),
        Field(name='ITEM72B_RECEIVES_SSI_UNDER_TITLE_XVI_SSI', type='string', startIndex=45, endIndex=46, required=True,
              validators=[]),
        Field(name='RELATIONSHIP_TO_HEAD_OF_HOUSEHOLD', type='number', startIndex=46, endIndex=48, required=True,
              validators=[]),
        Field(name='PARENT_WITH_MINOR_CHILD', type='string', startIndex=48, endIndex=49, required=True, validators=[
        ]),
        Field(name='EDUCATION_LEVEL', type='string', startIndex=49, endIndex=51, required=True, validators=[
        ]),
        Field(name='CITIZENSHIP_ALIENAGE', type='string', startIndex=51, endIndex=52, required=True, validators=[
        ]),
        Field(name='ITEM77A_SSI', type='string', startIndex=52, endIndex=56, required=False, validators=[]),
        Field(name='ITEM77B_OTHER_UNEARNED_INCOME', type='string', startIndex=56, endIndex=60, required=False,
              validators=[]),
    ],
)

child_two = RowSchema(
    model=TANF_T3,
    preparsing_validators=[
        validators.notEmpty(start=60, end=101),
    ],
    postparsing_validators=[],
    fields=[
        Field(name='RecordType', type='string', startIndex=0, endIndex=2, required=True, validators=[
        ]),
        Field(name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8, required=True, validators=[
        ]),
        Field(name='CASE_NUMBER', type='string', startIndex=8, endIndex=19, required=True, validators=[
        ]),
        Field(name='FAMILY_AFFILIATION', type='string', startIndex=60, endIndex=61, required=True, validators=[
        ]),
        Field(name='DOB', type='number', startIndex=60, endIndex=68, required=True, validators=[
        ]),
        Field(name='SSN', type='string', startIndex=68, endIndex=77, required=True, validators=[
        ]),
        Field(name='ITEM70A_HISPANIC_OR_LATINO', type='string', startIndex=77, endIndex=78, required=True, validators=[
        ]),
        Field(name='ITEM70B_AMERICAN_INDIAN_OR_ALASKA_NATIVE', type='string', startIndex=78, endIndex=79, required=True,
              validators=[]),
        Field(name='ITEM70C_ASIAN', type='string', startIndex=79, endIndex=80, required=True, validators=[
        ]),
        Field(name='ITEM70D_BLACK_OR_AFRICAN_AMERICAN', type='string', startIndex=81, endIndex=82, required=True,
              validators=[]),
        Field(name='ITEM70E_NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER', type='string', startIndex=82, endIndex=83,
              required=True, validators=[]),
        Field(name='ITEM70F_WHITE', type='string', startIndex=83, endIndex=84, required=True, validators=[
        ]),
        Field(name='GENDER', type='string', startIndex=84, endIndex=85, required=True, validators=[
        ]),
        Field(name='ITEM72A_RECEIVES_BENEFITS_UNDER_NON_SSA_PROGRAMS', type='string',
              startIndex=85, endIndex=86, required=True, validators=[]),
        Field(name='ITEM72B_RECEIVES_SSI_UNDER_TITLE_XVI_SSI', type='string', startIndex=86, endIndex=87, required=True,
              validators=[]),
        Field(name='RELATIONSHIP_TO_HEAD_OF_HOUSEHOLD', type='number', startIndex=87, endIndex=89, required=True,
              validators=[]),
        Field(name='PARENT_WITH_MINOR_CHILD', type='string', startIndex=89, endIndex=90, required=True, validators=[
        ]),
        Field(name='EDUCATION_LEVEL', type='string', startIndex=90, endIndex=92, required=True, validators=[
        ]),
        Field(name='CITIZENSHIP_ALIENAGE', type='string', startIndex=92, endIndex=93, required=True, validators=[
        ]),
        Field(name='ITEM77A_SSI', type='string', startIndex=93, endIndex=97, required=False, validators=[]),
        Field(name='ITEM77B_OTHER_UNEARNED_INCOME', type='string', startIndex=97, endIndex=101, required=False,
              validators=[]),
    ],
)

t3 = MultiRecordRowSchema(
    schemas=[
        child_one,
        child_two
    ]
)
