"""Schema for HEADER row of all submission types."""


from ...util import RowSchema, Field, SchemaManager
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T5


t5 = SchemaManager(
      schemas=[
        RowSchema(
          model=TANF_T5,
          preparsing_validators=[
              validators.hasLength(71),
          ],
          postparsing_validators=[],
          fields=[
              Field(item=1, name='RecordType', type='string', startIndex=0, endIndex=2,
                    required=True, validators=[]),
              Field(item=4, name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
                    required=True, validators=[]),
              Field(item=6, name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
                    required=True, validators=[]),
              Field(item=14, name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
                    required=True, validators=[]),
              Field(item=15, name='DATE_OF_BIRTH', type='number', startIndex=20, endIndex=28,
                    required=True, validators=[]),
              Field(item=16, name='SSN', type='string', startIndex=28, endIndex=37,
                    required=True, validators=[]),
              Field(item=17, name='RACE_HISPANIC', type='string', startIndex=37, endIndex=38,
                    required=True, validators=[]),
              Field(item=17, name='RACE_AMER_INDIAN', type='string', startIndex=38, endIndex=39,
                    required=True, validators=[]),
              Field(item=17, name='RACE_ASIAN', type='string', startIndex=39, endIndex=40,
                    required=True, validators=[]),
              Field(item=17, name='RACE_BLACK', type='string', startIndex=40, endIndex=41,
                    required=True, validators=[]),
              Field(item=17, name='RACE_HAWAIIAN', type='string', startIndex=41, endIndex=42,
                    required=True, validators=[]),
              Field(item=17, name='RACE_WHITE', type='string', startIndex=42, endIndex=43,
                    required=True, validators=[]),
              Field(item=18, name='GENDER', type='number', startIndex=43, endIndex=44,
                    required=True, validators=[]),
              Field(item=19, name='REC_OASDI_INSURANCE', type='string', startIndex=44, endIndex=45,
                    required=True, validators=[]),
              Field(item=19, name='REC_FEDERAL_DISABILITY', type='string', startIndex=45, endIndex=46,
                    required=True, validators=[]),
              Field(item=19, name='REC_AID_TOTALLY_DISABLED', type='string', startIndex=46, endIndex=47,
                    required=True, validators=[]),
              Field(item=19, name='REC_AID_AGED_BLIND', type='string', startIndex=47, endIndex=48,
                    required=True, validators=[]),
              Field(item=19, name='RECEIVE_SSI', type='string', startIndex=48, endIndex=49,
                    required=True, validators=[]),
              Field(item=20, name='MARITAL_STATUS', type='string', startIndex=49, endIndex=50,
                    required=True, validators=[]),
              Field(item=21, name='RELATIONSHIP_HOH', type='number', startIndex=50, endIndex=52,
                    required=True, validators=[]),
              Field(item=22, name='PARENT_WITH_MINOR_CHILD', type='string', startIndex=52, endIndex=53,
                    required=True, validators=[]),
              Field(item=23, name='NEEDS_PREGNANT_WOMAN', type='string', startIndex=53, endIndex=54,
                    required=True, validators=[]),
              Field(item=24, name='EDUCATION_LEVEL', type='string', startIndex=54, endIndex=56,
                    required=True, validators=[]),
              Field(item=25, name='CITIZENSHIP_STATUS', type='string', startIndex=56, endIndex=57,
                    required=True, validators=[]),
              Field(item=26, name='COUNTABLE_MONTH_FED_TIME', type='string', startIndex=57, endIndex=60,
                    required=True, validators=[]),
              Field(item=27, name='COUNTABLE_MONTHS_STATE_TRIBE', type='string', startIndex=60, endIndex=62,
                    required=True, validators=[]),
              Field(item=28, name='EMPLOYMENT_STATUS', type='string', startIndex=62, endIndex=63,
                    required=True, validators=[]),
              Field(item=29, name='AMOUNT_EARNED_INCOME', type='string', startIndex=63, endIndex=67,
                    required=True, validators=[]),
              Field(item=30, name='AMOUNT_UNEARNED_INCOME', type='string', startIndex=67, endIndex=71,
                    required=True, validators=[]),
          ],
        )
      ]
)
