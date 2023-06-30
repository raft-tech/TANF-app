"""Schema for HEADER row of all submission types."""


from ..cat3_validators import cat3_validate_t2
from ...util import RowSchema, Field
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T2


t2 = RowSchema(
    model=TANF_T2,
    preparsing_validators=[
        validators.hasLength(156),
    ],
    postparsing_validators=[
            cat3_validate_t2,
            validators.if_then_validator(
                  condition_field='DATE_OF_BIRTH', condition_function=validators.matches('99999999'),
                  result_field='FAMILY_AFFILIATION', result_function=validators.isInLimits(2, 5),
            ),
            validators.if_then_validator(
                  condition_field='SSN', condition_function=validators.matches('999999999'),
                  result_field='FAMILY_AFFILIATION', result_function=validators.isInLimits(2, 5),
            ),
            validators.if_then_validator(
                  condition_field='RACE_HISPANIC', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 4),
                  result_field='RACE_HISPANIC', result_function=validators.oneOf([1, 2]),
            ),
            validators.if_then_validator(
                  condition_field='RACE_AMER_INDIAN', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 4),
                  result_field='RACE_AMER_INDIAN', result_function=validators.oneOf([1, 2]),
            ),
            validators.if_then_validator(
                  condition_field='RACE_ASIAN', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 4),
                  result_field='RACE_ASIAN', result_function=validators.oneOf([1, 2]),
            ),
            validators.if_then_validator(
                  condition_field='RACE_BLACK', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 4),
                  result_field='RACE_BLACK', result_function=validators.oneOf([1, 2]),
            ),
            validators.if_then_validator(
                  condition_field='RACE_HAWAIIAN', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 4),
                  result_field='RACE_HAWAIIAN', result_function=validators.oneOf([1, 2]),
            ),
            validators.if_then_validator(
                  condition_field='RACE_WHITE', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 4),
                  result_field='RACE_WHITE', result_function=validators.oneOf([1, 2]),
            ),
            validators.if_then_validator(
                  condition_field='MARITAL_STATUS', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 4),
                result_field='MARITAL_STATUS', result_function=validators.oneOf([1, 2, 3, 4, 5]),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf([1, 2, 4]),
                  result_field='PARENT_WITH_MINOR_CHILD', result_function=validators.isInLimits(1, 3),
            ),
            validators.if_then_validator(
                condition_field='PARENT_WITH_MINOR_CHILD', condition_function=validators.isBlank(),
                result_field='FAMILY_AFFILIATION', result_function=validators.oneOf([3, 5]),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(2, 5),
                  result_field='EDUCATION_LEVEL', result_function=validators.oneOf(
                      [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 98, 99]
                  )
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(2, 5),
                  result_field='EDUCATION_LEVEL', result_function=validators.oneOf(
                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 98]
                  )
            ),
            validators.if_then_validator(
                  condition_field='EDUCATION_LEVEL', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='CITIZENSHIP_STATUS', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 4),
                  result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf([1, 2, 9]),
            ),
            validators.if_then_validator(
                  condition_field='COOPERATION_CHILD_SUPPORT', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='EMPLOYMENT_STATUS', result_function=validators.between(1, 3),
            ),
            validators.if_then_validator(
                  condition_field='EMPLYMENT_STATUS', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.matches(5),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf([1, 2]),
                  result_field='WORK_PART_STATUS', result_function=validators.oneOf(
                    [1, 2,
                     5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                     99]
                  )
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='UNSUB_EMPLOYMENT', result_function=validators.isLargerThanOrEqualTo(0),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='SUB_PRIVATE_EMPLOYMENT', result_function=validators.isLargerThanOrEqualTo(0),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='SUB_PUBLIC_EMPLOYMENT', result_function=validators.isLargerThanOrEqualTo(0),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='OJT', result_function=validators.isLargerThanOrEqualTo(0),
            ),
            validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                  result_field='NEEDS_PREGNANT_WOMAN', result_function=validators.oneOf([1, 2]),
            ),
            validators.if_then_validator(
                  condition_field='NEEDS_PREGNANT_WOMAN', condition_function=validators.isBlank(),
                  result_field='FAMILY_AFFILIATION', result_function=validators.oneOf([2, 5]),
            )
        ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="4", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              required=True, validators=[
                  validators.month_year_yearIsLargerThan(1998),
                  validators.month_year_monthIsValid(),
              ]),
        Field(item="6", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              required=True, validators=[
                              validators.notEmpty(),
              ]),
        Field(item="30", name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
              required=True, validators=[
                              validators.isInLimits(1, 5),
              ]),
        Field(item="31", name='NONCUSTODIAL_PARENT', type='number', startIndex=20, endIndex=21,
              required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="32", name='DATE_OF_BIRTH', type='number', startIndex=21, endIndex=29,
              required=True, validators=[
                  validators.notEmpty(),
                  validators.notZero(8),
              ]),
        Field(item="33", name='SSN', type='string', startIndex=29, endIndex=38,
              required=True, validators=[
                  validators.notEmpty(),
                  validators.notZero(9),
              ]),
        Field(item="34A", name='RACE_HISPANIC', type='string', startIndex=38, endIndex=39,
              required=True, validators=[]),
        Field(item="34B", name='RACE_AMER_INDIAN', type='string', startIndex=39, endIndex=40,
              required=True, validators=[]),
        Field(item="34C", name='RACE_ASIAN', type='string', startIndex=40, endIndex=41,
              required=True, validators=[]),
        Field(item="34D", name='RACE_BLACK', type='string', startIndex=41, endIndex=42,
              required=True, validators=[]),
        Field(item="34E", name='RACE_HAWAIIAN', type='string', startIndex=42, endIndex=43,
              required=True, validators=[]),
        Field(item="34F", name='RACE_WHITE', type='string', startIndex=43, endIndex=44,
              required=True, validators=[]),
        Field(item="35", name='GENDER', type='number', startIndex=44, endIndex=45,
              required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="36A", name='FED_OASDI_PROGRAM', type='string', startIndex=45, endIndex=46,
              required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="36B", name='FED_DISABILITY_STATUS', type='string', startIndex=46, endIndex=47,
              required=True, validators=[
                  validators.oneOf([1, 2])
              ]),
        Field(item="36C", name='DISABLED_TITLE_XIVAPDT', type='string', startIndex=47, endIndex=48,
              required=True, validators=[
                  validators.or_validators(
                      validators.oneOf([1, 2]),
                      validators.isBlank()
                  )
              ]),
        Field(item="36D", name='AID_AGED_BLIND', type='string', startIndex=48, endIndex=49,
              required=True, validators=[
                  validators.or_validators(
                      validators.oneOf([1, 2]),
                      validators.isBlank()
                  )
              ]),
        Field(item="36E", name='RECEIVE_SSI', type='string', startIndex=49, endIndex=50,
              required=True, validators=[
                  validators.or_validators(
                      validators.oneOf([1, 2]),
                      validators.isBlank()
                  )
              ]),
        Field(item="37", name='MARITAL_STATUS', type='string', startIndex=50, endIndex=51,
              required=True, validators=[]),
        Field(item="38", name='RELATIONSHIP_HOH', type='number', startIndex=51, endIndex=53,
              required=True, validators=[
                  validators.isInLimits(1, 10),
              ]),
        Field(item="39", name='PARENT_WITH_MINOR_CHILD', type='string', startIndex=53, endIndex=54,
              required=True, validators=[]),
        Field(item="40", name='NEEDS_PREGNANT_WOMAN', type='string', startIndex=54, endIndex=55,
              required=True, validators=[]),
        Field(item="41", name='EDUCATION_LEVEL', type='string', startIndex=55, endIndex=57,
              required=True, validators=[]),
        Field(item="42", name='CITIZENSHIP_STATUS', type='string', startIndex=57, endIndex=58,
              required=True, validators=[]),
        Field(item="43", name='COOPERATION_CHILD_SUPPORT', type='string', startIndex=58, endIndex=59,
              required=True, validators=[
                  validators.oneOf([1, 2, 9]),
              ]),
        Field(item="44", name='MONTHS_FED_TIME_LIMIT', type='string', startIndex=59, endIndex=62,
              required=True, validators=[]),
        Field(item="45", name='MONTHS_STATE_TIME_LIMIT', type='string', startIndex=62, endIndex=64,
              required=True, validators=[]),
        Field(item="46", name='CURRENT_MONTH_STATE_EXEMPT', type='string', startIndex=64, endIndex=65,
              required=True, validators=[]),
        Field(item="47", name='EMPLOYMENT_STATUS', type='string', startIndex=65, endIndex=66,
              required=True, validators=[]),
        Field(item="48", name='WORK_ELIGIBLE_INDICATOR', type='string', startIndex=66, endIndex=68,
              required=True, validators=[]),
        Field(item="49", name='WORK_PART_STATUS', type='string', startIndex=68, endIndex=70,
              required=True, validators=[]),
        Field(item="50", name='UNSUB_EMPLOYMENT', type='string', startIndex=70, endIndex=72,
              required=True, validators=[]),
        Field(item="51", name='SUB_PRIVATE_EMPLOYMENT', type='string', startIndex=72, endIndex=74,
              required=True, validators=[]),
        Field(item="52", name='SUB_PUBLIC_EMPLOYMENT', type='string', startIndex=74, endIndex=76,
              required=True, validators=[]),
        Field(item="53A", name='WORK_EXPERIENCE_HOP', type='string', startIndex=76, endIndex=78,
              required=True, validators=[]),
        Field(item="53B", name='WORK_EXPERIENCE_EA', type='string', startIndex=78, endIndex=80,
              required=True, validators=[]),
        Field(item="53C", name='WORK_EXPERIENCE_HOL', type='string', startIndex=80, endIndex=82,
              required=True, validators=[]),
        Field(item="54", name='OJT', type='string', startIndex=82, endIndex=84,
              required=True, validators=[]),
        Field(item="55A", name='JOB_SEARCH_HOP', type='string', startIndex=84, endIndex=86,
              required=True, validators=[]),
        Field(item="55B", name='JOB_SEARCH_EA', type='string', startIndex=86, endIndex=88,
              required=True, validators=[]),
        Field(item="55C", name='JOB_SEARCH_HOL', type='string', startIndex=88, endIndex=90,
              required=True, validators=[]),
        Field(item="56A", name='COMM_SERVICES_HOP', type='string', startIndex=90, endIndex=92,
              required=True, validators=[]),
        Field(item="56B", name='COMM_SERVICES_EA', type='string', startIndex=92, endIndex=94,
              required=True, validators=[]),
        Field(item="56C", name='COMM_SERVICES_HOL', type='string', startIndex=94, endIndex=96,
              required=True, validators=[]),
        Field(item="57A", name='VOCATIONAL_ED_TRAINING_HOP', type='string', startIndex=96, endIndex=98,
              required=False, validators=[]),
        Field(item="57B", name='VOCATIONAL_ED_TRAINING_EA', type='string', startIndex=98, endIndex=100,
              required=False, validators=[]),
        Field(item="57C", name='VOCATIONAL_ED_TRAINING_HOL', type='string', startIndex=100, endIndex=102,
              required=False, validators=[]),
        Field(item="58A", name='JOB_SKILLS_TRAINING_HOP', type='string', startIndex=102, endIndex=104,
              required=False, validators=[]),
        Field(item="58B", name='JOB_SKILLS_TRAINING_EA', type='string', startIndex=104, endIndex=106,
              required=False, validators=[]),
        Field(item="58C", name='JOB_SKILLS_TRAINING_HOL', type='string', startIndex=106, endIndex=108,
              required=False, validators=[]),
        Field(item="59A", name='ED_NO_HIGH_SCHOOL_DIPL_HOP', type='string', startIndex=108, endIndex=110,
              required=False, validators=[]),
        Field(item="59B", name='ED_NO_HIGH_SCHOOL_DIPL_EA', type='string', startIndex=110, endIndex=112,
              required=False, validators=[]),
        Field(item="59C", name='ED_NO_HIGH_SCHOOL_DIPL_HOL', type='string', startIndex=112, endIndex=114,
              required=False, validators=[]),
        Field(item="60A", name='SCHOOL_ATTENDENCE_HOP', type='string', startIndex=114, endIndex=116,
              required=False, validators=[]),
        Field(item="60B", name='SCHOOL_ATTENDENCE_EA', type='string', startIndex=116, endIndex=118,
              required=False, validators=[]),
        Field(item="60C", name='SCHOOL_ATTENDENCE_HOL', type='string', startIndex=118, endIndex=120,
              required=False, validators=[]),
        Field(item="61A", name='PROVIDE_CC_HOP', type='string', startIndex=120, endIndex=122,
              required=False, validators=[]),
        Field(item="61B", name='PROVIDE_CC_EA', type='string', startIndex=122, endIndex=124,
              required=False, validators=[]),
        Field(item="61C", name='PROVIDE_CC_HOL', type='string', startIndex=124, endIndex=126,
              required=False, validators=[]),
        Field(item="62", name='OTHER_WORK_ACTIVITIES', type='string', startIndex=126, endIndex=128,
              required=False, validators=[]),
        Field(item="63", name='DEEMED_HOURS_FOR_OVERALL', type='string', startIndex=128, endIndex=130,
              required=False, validators=[]),
        Field(item="64", name='DEEMED_HOURS_FOR_TWO_PARENT', type='string', startIndex=130, endIndex=132,
              required=False, validators=[]),
        Field(item="65", name='EARNED_INCOME', type='string', startIndex=132, endIndex=136,
              required=False, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item="66A", name='UNEARNED_INCOME_TAX_CREDIT', type='string', startIndex=136, endIndex=140,
              required=False, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item="66B", name='UNEARNED_SOCIAL_SECURITY', type='string', startIndex=140, endIndex=144,
              required=False, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item="66C", name='UNEARNED_SSI', type='string', startIndex=144, endIndex=148,
              required=False, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item="66D", name='UNEARNED_WORKERS_COMP', type='string', startIndex=148, endIndex=152,
              required=False, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item="66E", name='OTHER_UNEARNED_INCOME', type='string', startIndex=152, endIndex=156,
              required=False, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
    ],
)
