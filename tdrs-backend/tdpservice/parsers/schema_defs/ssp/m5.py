"""Schema for SSP M1 record type."""


from ...util import SchemaManager
from ...transforms import ssp_ssn_decryption_func
from ...fields import TransformField, Field
from ...row_schema import RowSchema
from ... import validators
from tdpservice.search_indexes.models.ssp import SSP_M5


m5 = SchemaManager(
      schemas=[
        RowSchema(
          model=SSP_M5,
          preparsing_validators=[
              validators.hasLength(66),
          ],
          postparsing_validators=[],
          fields=[
              Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
                    required=True, validators=[]),
              Field(item="3", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
                    required=True, validators=[validators.dateYearIsLargerThan(1998), 
                                               validators.dateMonthIsValid(),]),
              Field(item="5", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
                    required=True, validators=[validators.isAlphaNumeric()]),
              Field(item="26", name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
                    required=True, validators=[]),
              Field(item="28", name='DATE_OF_BIRTH', type='string', startIndex=20, endIndex=28,
                    required=True, validators=[validators.dateYearIsLargerThan(1998),
                                               validators.dateMonthIsValid(),]),
              TransformField(transform_func=ssp_ssn_decryption_func, item="29", name='SSN', type='string',
                             startIndex=28, endIndex=37, required=True, validators=[validators.validateSSN()],
                             is_encrypted=False),
              Field(item="30A", name='RACE_HISPANIC', type='number', startIndex=37, endIndex=38, required=True,
                    validators=[validators.isInLimits(0, 2)]),
              Field(item="30B", name='RACE_AMER_INDIAN', type='number', startIndex=38, endIndex=39,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="30C", name='RACE_ASIAN', type='number', startIndex=39, endIndex=40,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="30D", name='RACE_BLACK', type='number', startIndex=40, endIndex=41,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="30E", name='RACE_HAWAIIAN', type='number', startIndex=41, endIndex=42,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="30F", name='RACE_WHITE', type='number', startIndex=42, endIndex=43,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="31", name='GENDER', type='number', startIndex=43, endIndex=44,
                    required=True, validators=[validators.isInLimits(0, 9)]),
              Field(item="28", name='REC_OASDI_INSURANCE', type='number', startIndex=44, endIndex=45,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="28", name='REC_FEDERAL_DISABILITY', type='number', startIndex=45, endIndex=46,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="28", name='REC_AID_TOTALLY_DISABLED', type='number', startIndex=46, endIndex=47,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="28", name='REC_AID_AGED_BLIND', type='number', startIndex=47, endIndex=48,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="28", name='REC_SSI', type='number', startIndex=48, endIndex=49,
                    required=True, validators=[validators.isInLimits(1, 2)]),
              Field(item="28", name='MARITAL_STATUS', type='number', startIndex=49, endIndex=50,
                    required=True, validators=[validators.isInLimits(0, 5)]),
              Field(item="28", name='RELATIONSHIP_HOH', type='string', startIndex=50, endIndex=52,
                    required=True, validators=[validators.isInStringRange(1, 10)]),
              Field(item="28", name='PARENT_MINOR_CHILD', type='number', startIndex=52, endIndex=53,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="28", name='NEEDS_OF_PREGNANT_WOMAN', type='number', startIndex=53, endIndex=54,
                    required=True, validators=[validators.isInLimits(0, 9)]),
              Field(item="28", name='EDUCATION_LEVEL', type='string', startIndex=54, endIndex=56,
                    required=True, validators=[validators.or_validators(validators.isInStringRange(0, 16),
                                                                        validators.isInStringRange(98, 99))]),
              Field(item="28", name='CITIZENSHIP_STATUS', type='number', startIndex=56, endIndex=57,
                    required=True, validators=[validators.or_validators(validators.isInLimits(0, 3),
                                                                        validators.matches(9))]),
              Field(item="28", name='EMPLOYMENT_STATUS', type='number', startIndex=57, endIndex=58,
                    required=True, validators=[validators.isInLimits(0, 3)]),
              Field(item="28", name='AMOUNT_EARNED_INCOME', type='string', startIndex=58, endIndex=62,
                    required=True, validators=[validators.isInStringRange(0, 9999)]),
              Field(item="28", name='AMOUNT_UNEARNED_INCOME', type='string', startIndex=62, endIndex=66,
                    required=True, validators=[validators.isInStringRange(0, 9999)]),
          ],
        )
      ]
  )
