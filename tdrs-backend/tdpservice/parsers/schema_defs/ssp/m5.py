"""Schema for SSP M1 record type."""


from tdpservice.parsers.util import SchemaManager
from tdpservice.parsers.transforms import ssp_ssn_decryption_func
from tdpservice.parsers.fields import TransformField, Field
from tdpservice.parsers.row_schema import RowSchema
from tdpservice.parsers import validators
from tdpservice.search_indexes.models.ssp import SSP_M5


m5 = SchemaManager(
      schemas=[
        RowSchema(
          model=SSP_M5,
          preparsing_validators=[
              validators.hasLength(66),
          ],
          postparsing_validators=[
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                        result_field='SSN', result_function=validators.validateSSN(),
                  ),
              validators.validate__FAM_AFF__SSN(),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='RACE_HISPANIC', result_function=validators.isInLimits(1, 2),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='RACE_AMER_INDIAN', result_function=validators.isInLimits(1, 2),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='RACE_ASIAN', result_function=validators.isInLimits(1, 2),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='RACE_BLACK', result_function=validators.isInLimits(1, 2),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='RACE_HAWAIIAN', result_function=validators.isInLimits(1, 2),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='RACE_WHITE', result_function=validators.isInLimits(1, 2),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='MARITAL_STATUS', result_function=validators.isInLimits(1, 5),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 2),
                        result_field='PARENT_MINOR_CHILD', result_function=validators.isInLimits(1, 3),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                        result_field='EDUCATION_LEVEL', result_function=validators.or_validators(
                            validators.isInStringRange(1, 16), validators.isInStringRange(98, 99)),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                        result_field='CITIZENSHIP_STATUS', result_function=validators.isInLimits(1, 3),
                  ),
              validators.if_then_validator(
                        condition_field='DATE_OF_BIRTH', condition_function=validators.olderThan(18),
                        result_field='REC_OASDI_INSURANCE', result_function=validators.isInLimits(1, 2),
                  ),
              validators.if_then_validator(
                        condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                        result_field='REC_FEDERAL_DISABILITY', result_function=validators.isInLimits(1, 2),
                  ),
          ],
          fields=[
              Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
                    required=True, validators=[]),
              Field(item="3", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
                    required=True, validators=[validators.dateYearIsLargerThan(1998),
                                               validators.dateMonthIsValid(),]),
              Field(item="5", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
                    required=True, validators=[validators.isAlphaNumeric()]),
              Field(item="13", name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
                    required=True, validators=[validators.isInLimits(1, 5)]),
              Field(item="14", name='DATE_OF_BIRTH', type='string', startIndex=20, endIndex=28,
                    required=True, validators=[validators.dateYearIsLargerThan(1900),
                                               validators.dateMonthIsValid(),]),
              TransformField(transform_func=ssp_ssn_decryption_func, item="15", name='SSN', type='string',
                             startIndex=28, endIndex=37, required=True, validators=[validators.validateSSN()],
                             is_encrypted=False),
              Field(item="16A", name='RACE_HISPANIC', type='number', startIndex=37, endIndex=38, required=False,
                    validators=[validators.validateRace()]),
              Field(item="16B", name='RACE_AMER_INDIAN', type='number', startIndex=38, endIndex=39,
                    required=False, validators=[validators.validateRace()]),
              Field(item="16C", name='RACE_ASIAN', type='number', startIndex=39, endIndex=40,
                    required=False, validators=[validators.validateRace()]),
              Field(item="16D", name='RACE_BLACK', type='number', startIndex=40, endIndex=41,
                    required=False, validators=[validators.validateRace()]),
              Field(item="16E", name='RACE_HAWAIIAN', type='number', startIndex=41, endIndex=42,
                    required=False, validators=[validators.validateRace()]),
              Field(item="16F", name='RACE_WHITE', type='number', startIndex=42, endIndex=43,
                    required=False, validators=[validators.validateRace()]),
              Field(item="17", name='GENDER', type='number', startIndex=43, endIndex=44,
                    required=True, validators=[validators.isInLimits(0, 9)]),
              Field(item="18A", name='REC_OASDI_INSURANCE', type='number', startIndex=44, endIndex=45,
                    required=True, validators=[validators.isInLimits(0, 2)]),
              Field(item="18B", name='REC_FEDERAL_DISABILITY', type='number', startIndex=45, endIndex=46,
                    required=False, validators=[validators.isInLimits(0, 2)]),
              Field(item="18C", name='REC_AID_TOTALLY_DISABLED', type='number', startIndex=46, endIndex=47,
                    required=False, validators=[validators.isInLimits(0, 2)]),
              Field(item="18D", name='REC_AID_AGED_BLIND', type='number', startIndex=47, endIndex=48,
                    required=False, validators=[validators.isInLimits(0, 2)]),
              Field(item="18E", name='REC_SSI', type='number', startIndex=48, endIndex=49,
                    required=True, validators=[validators.isInLimits(1, 2)]),
              Field(item="19", name='MARITAL_STATUS', type='number', startIndex=49, endIndex=50,
                    required=False, validators=[validators.isInLimits(0, 5)]),
              Field(item="20", name='RELATIONSHIP_HOH', type='string', startIndex=50, endIndex=52,
                    required=True, validators=[validators.isInStringRange(1, 10)]),
              Field(item="21", name='PARENT_MINOR_CHILD', type='number', startIndex=52, endIndex=53,
                    required=False, validators=[validators.isInLimits(0, 2)]),
              Field(item="22", name='NEEDS_OF_PREGNANT_WOMAN', type='number', startIndex=53, endIndex=54,
                    required=False, validators=[validators.isInLimits(0, 9)]),
              Field(item="23", name='EDUCATION_LEVEL', type='string', startIndex=54, endIndex=56,
                    required=False, validators=[validators.or_validators(validators.isInStringRange(0, 16),
                                                                        validators.isInStringRange(98, 99))]),
              Field(item="24", name='CITIZENSHIP_STATUS', type='number', startIndex=56, endIndex=57,
                    required=False, validators=[validators.or_validators(validators.isInLimits(0, 3),
                                                                        validators.matches(9))]),
              Field(item="25", name='EMPLOYMENT_STATUS', type='number', startIndex=57, endIndex=58,
                    required=False, validators=[validators.isInLimits(0, 3)]),
              Field(item="26", name='AMOUNT_EARNED_INCOME', type='string', startIndex=58, endIndex=62,
                    required=True, validators=[validators.isInStringRange(0, 9999)]),
              Field(item="27", name='AMOUNT_UNEARNED_INCOME', type='string', startIndex=62, endIndex=66,
                    required=True, validators=[validators.isInStringRange(0, 9999)]),
          ],
        )
      ]
  )
