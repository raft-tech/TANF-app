"""Schema for HEADER row of all submission types."""


from ...util import SchemaManager
from ...fields import EncryptedField, Field, tanf_ssn_decryption_func
from ...row_schema import RowSchema
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T5


t5 = SchemaManager(
      schemas=[
        RowSchema(
          model=TANF_T5,
          preparsing_validators=[
              validators.hasLength(71),
          ],
          postparsing_validators=[
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.notMatches(1),
                  result_field='SSN', result_function=validators.isNumber()
                  ),
              validators.validate__FAM_AFF__SSN(),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='RACE_HISPANIC', result_function=validators.oneOf(["1", "2"])
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='RACE_AMER_INDIAN', result_function=validators.oneOf(["1", "2"])
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='RACE_ASIAN', result_function=validators.oneOf(["1", "2"])
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='RACE_BLACK', result_function=validators.oneOf(["1", "2"])
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='RACE_HAWAIIAN', result_function=validators.oneOf(["1", "2"])
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='RACE_WHITE', result_function=validators.oneOf(["1", "2"])
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='MARITAL_STATUS', result_function=validators.oneOf(["1", "2", "3", "4", "5"])
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 2),
                  result_field='PARENT_MINOR_CHILD', result_function=validators.oneOf(["1", "2", "3"])
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='EDUCATION_LEVEL', result_function=validators.or_validators(
                      validators.isInStringRange(1, 16, 2),
                      validators.isInStringRange(98, 99)
                      )
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf(["1", "2"])
                  ),
              validators.validate__FAM_AFF__HOH__FEDTIME(),
              validators.if_then_validator(
                  condition_field='DATE_OF_BIRTH', condition_function=validators.month_year_yearIsLargerThan(19),
                  result_field='REC_OASDI_INSURANCE', result_function=validators.oneOf(["1", "2"])
                  ),
              validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='REC_FEDERAL_DISABILITY', result_function=validators.oneOf(["1", "2"])
                  ),
                ],
          fields=[
              Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
                    required=True, validators=[]),
              Field(item="4", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
                    required=True, validators=[validators.month_year_yearIsLargerThan(1998),
                                               validators.month_year_monthIsValid()]),
              Field(item="6", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
                    required=True, validators=[validators.isAlphaNumeric(),
                                               validators.notMatches('_'*11),
                                               validators.notEmpty()]),
              Field(item="14", name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
                    required=True, validators=[validators.isInLimits(1, 5)]),
              Field(item="15", name='DATE_OF_BIRTH', type='number', startIndex=20, endIndex=28,
                    required=True, validators=[validators.isLargerThan(0)]),
              EncryptedField(decryption_func=tanf_ssn_decryption_func, item="16", name='SSN', type='string',
                             startIndex=28, endIndex=37, required=True, validators=[validators.isNumber()]),
              Field(item="17A", name='RACE_HISPANIC', type='string', startIndex=37, endIndex=38,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="17B", name='RACE_AMER_INDIAN', type='string', startIndex=38, endIndex=39,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="17C", name='RACE_ASIAN', type='string', startIndex=39, endIndex=40,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="17D", name='RACE_BLACK', type='string', startIndex=40, endIndex=41,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="17E", name='RACE_HAWAIIAN', type='string', startIndex=41, endIndex=42,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="17F", name='RACE_WHITE', type='string', startIndex=42, endIndex=43,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="18", name='GENDER', type='number', startIndex=43, endIndex=44,
                    required=True, validators=[validators.isInLimits(0, 9)]),
              Field(item="19A", name='REC_OASDI_INSURANCE', type='string', startIndex=44, endIndex=45,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="19B", name='REC_FEDERAL_DISABILITY', type='string', startIndex=45, endIndex=46,
                    required=True, validators=[validators.oneOf(["1", "2"])]),
              Field(item="19C", name='REC_AID_TOTALLY_DISABLED', type='string', startIndex=46, endIndex=47,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="19D", name='REC_AID_AGED_BLIND', type='string', startIndex=47, endIndex=48,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="19E", name='RECEIVE_SSI', type='string', startIndex=48, endIndex=49,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="20", name='MARITAL_STATUS', type='string', startIndex=49, endIndex=50,
                    required=True, validators=[validators.oneOf(["0", "1", "2", "3", "4", "5"])]),
              Field(item="21", name='RELATIONSHIP_HOH', type='number', startIndex=50, endIndex=52,
                    required=True, validators=[validators.isInLimits(1, 10)]),
              Field(item="22", name='PARENT_MINOR_CHILD', type='string', startIndex=52, endIndex=53,
                    required=True, validators=[validators.oneOf(["0", "1", "2"])]),
              Field(item="23", name='NEEDS_PREGNANT_WOMAN', type='string', startIndex=53, endIndex=54,
                    required=True, validators=[validators.oneOf(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])]),
              Field(item="24", name='EDUCATION_LEVEL', type='string', startIndex=54, endIndex=56,
                    required=True, validators=[validators.or_validators(validators.isInStringRange(0, 16, 2),
                                                                        validators.isInStringRange(98, 99))]),
              Field(item="25", name='CITIZENSHIP_STATUS', type='string', startIndex=56, endIndex=57,
                    required=True, validators=[validators.oneOf(["0", "1", "2", "9"])]),
              Field(item="26", name='COUNTABLE_MONTH_FED_TIME', type='string', startIndex=57, endIndex=60,
                    required=True, validators=[validators.isInStringRange(0, 999, 3)]),
              Field(item="27", name='COUNTABLE_MONTHS_STATE_TRIBE', type='string', startIndex=60, endIndex=62,
                    required=True, validators=[validators.isInStringRange(0, 99, 2)]),
              Field(item="28", name='EMPLOYMENT_STATUS', type='string', startIndex=62, endIndex=63,
                    required=True, validators=[validators.oneOf(["0", "1", "2", "3"])]),
              Field(item="29", name='AMOUNT_EARNED_INCOME', type='string', startIndex=63, endIndex=67,
                    required=True, validators=[validators.isInStringRange(0, 9999, 4)]),
              Field(item="30", name='AMOUNT_UNEARNED_INCOME', type='string', startIndex=67, endIndex=71,
                    required=True, validators=[validators.isInStringRange(0, 9999, 4)]),
          ],
        )
      ]
)
