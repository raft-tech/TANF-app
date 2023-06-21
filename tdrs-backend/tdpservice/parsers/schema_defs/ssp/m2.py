"""Schema for SSP M1 record type."""


from ...util import RowSchema, Field, SchemaManager
from ... import validators
from tdpservice.search_indexes.models.ssp import SSP_M2


m2 = SchemaManager(
      schemas=[
        RowSchema(
          model=SSP_M2,
          preparsing_validators=[
              validators.hasLength(150),
          ],
          postparsing_validators=[],
          fields=[
              Field(item=1, name='RecordType', type='string', startIndex=0, endIndex=2,
                    required=True, validators=[]),
              Field(item=2, name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
                    required=True, validators=[]),
              Field(item=3, name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
                    required=True, validators=[]),
              Field(item=4, name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
                    required=True, validators=[]),
              Field(item=5, name='NONCUSTODIAL_PARENT', type='number', startIndex=20, endIndex=21,
                    required=True, validators=[]),
              Field(item=6, name='DATE_OF_BIRTH', type='string', startIndex=21, endIndex=29,
                    required=True, validators=[]),
              Field(item=7, name='SSN', type='string', startIndex=29, endIndex=38,
                    required=True, validators=[]),
              Field(item=8, name='RACE_HISPANIC', type='number', startIndex=38, endIndex=39,
                    required=True, validators=[]),
              Field(item=9, name='RACE_AMER_INDIAN', type='number', startIndex=39, endIndex=40,
                    required=True, validators=[]),
              Field(item=10, name='RACE_ASIAN', type='number', startIndex=40, endIndex=41,
                    required=True, validators=[]),
              Field(item=11, name='RACE_BLACK', type='number', startIndex=41, endIndex=42,
                    required=True, validators=[]),
              Field(item=12, name='RACE_HAWAIIAN', type='number', startIndex=42, endIndex=43,
                    required=True, validators=[]),
              Field(item=13, name='RACE_WHITE', type='number', startIndex=43, endIndex=44,
                    required=True, validators=[]),
              Field(item=14, name='GENDER', type='number', startIndex=44, endIndex=45,
                    required=True, validators=[]),
              Field(item=15, name='FED_OASDI_PROGRAM', type='number', startIndex=45, endIndex=46,
                    required=True, validators=[]),
              Field(item=16, name='FED_DISABILITY_STATUS', type='number', startIndex=46, endIndex=47,
                    required=True, validators=[]),
              Field(item=17, name='DISABLED_TITLE_XIVAPDT', type='number', startIndex=47, endIndex=48,
                    required=True, validators=[]),
              Field(item=18, name='AID_AGED_BLIND', type='number', startIndex=48, endIndex=49,
                    required=True, validators=[]),
              Field(item=19, name='RECEIVE_SSI', type='number', startIndex=49, endIndex=50,
                    required=True, validators=[]),
              Field(item=20, name='MARITAL_STATUS', type='number', startIndex=50, endIndex=51,
                    required=True, validators=[]),
              Field(item=21, name='RELATIONSHIP_HOH', type='number', startIndex=51, endIndex=53,
                    required=True, validators=[]),
              Field(item=22, name='PARENT_MINOR_CHILD', type='number', startIndex=53, endIndex=54,
                    required=True, validators=[]),
              Field(item=23, name='NEEDS_PREGNANT_WOMAN', type='number', startIndex=54, endIndex=55,
                    required=True, validators=[]),
              Field(item=24, name='EDUCATION_LEVEL', type='number', startIndex=55, endIndex=57,
                    required=True, validators=[]),
              Field(item=25, name='CITIZENSHIP_STATUS', type='number', startIndex=57, endIndex=58,
                    required=True, validators=[]),
              Field(item=26, name='COOPERATION_CHILD_SUPPORT', type='number', startIndex=58, endIndex=59,
                    required=True, validators=[]),
              Field(item=27, name='EMPLOYMENT_STATUS', type='number', startIndex=59, endIndex=60,
                    required=True, validators=[]),
              Field(item=28, name='WORK_ELIGIBLE_INDICATOR', type='number', startIndex=60, endIndex=62,
                    required=True, validators=[]),
              Field(item=29, name='WORK_PART_STATUS', type='number', startIndex=62, endIndex=64,
                    required=True, validators=[]),
              Field(item=30, name='UNSUB_EMPLOYMENT', type='number', startIndex=64, endIndex=66,
                    required=True, validators=[]),
              Field(item=31, name='SUB_PRIVATE_EMPLOYMENT', type='number', startIndex=66, endIndex=68,
                    required=True, validators=[]),
              Field(item=32, name='SUB_PUBLIC_EMPLOYMENT', type='number', startIndex=68, endIndex=70,
                    required=True, validators=[]),
              Field(item=33, name='WORK_EXPERIENCE_HOP', type='number', startIndex=70, endIndex=72,
                    required=True, validators=[]),
              Field(item=34, name='WORK_EXPERIENCE_EA', type='number', startIndex=72, endIndex=74,
                    required=True, validators=[]),
              Field(item=35, name='WORK_EXPERIENCE_HOL', type='number', startIndex=74, endIndex=76,
                    required=True, validators=[]),
              Field(item=36, name='OJT', type='number', startIndex=76, endIndex=78,
                    required=True, validators=[]),
              Field(item=37, name='JOB_SEARCH_HOP', type='number', startIndex=78, endIndex=80,
                    required=True, validators=[]),
              Field(item=38, name='JOB_SEARCH_EA', type='number', startIndex=80, endIndex=82,
                    required=True, validators=[]),
              Field(item=39, name='JOB_SEARCH_HOL', type='number', startIndex=82, endIndex=84,
                    required=True, validators=[]),
              Field(item=40, name='COMM_SERVICES_HOP', type='number', startIndex=84, endIndex=86,
                    required=True, validators=[]),
              Field(item=41, name='COMM_SERVICES_EA', type='number', startIndex=86, endIndex=88,
                    required=True, validators=[]),
              Field(item=42, name='COMM_SERVICES_HOL', type='number', startIndex=88, endIndex=90,
                    required=True, validators=[]),
              Field(item=43, name='VOCATIONAL_ED_TRAINING_HOP', type='number', startIndex=90, endIndex=92,
                    required=True, validators=[]),
              Field(item=44, name='VOCATIONAL_ED_TRAINING_EA', type='number', startIndex=92, endIndex=94,
                    required=True, validators=[]),
              Field(item=45, name='VOCATIONAL_ED_TRAINING_HOL', type='number', startIndex=94, endIndex=96,
                    required=True, validators=[]),
              Field(item=46, name='JOB_SKILLS_TRAINING_HOP', type='number', startIndex=96, endIndex=98,
                    required=True, validators=[]),
              Field(item=47, name='JOB_SKILLS_TRAINING_EA', type='number', startIndex=98, endIndex=100,
                    required=True, validators=[]),
              Field(item=48, name='JOB_SKILLS_TRAINING_HOL', type='number', startIndex=100, endIndex=102,
                    required=True, validators=[]),
              Field(item=49, name='ED_NO_HIGH_SCHOOL_DIPL_HOP', type='number', startIndex=102, endIndex=104,
                    required=True, validators=[]),
              Field(item=50, name='ED_NO_HIGH_SCHOOL_DIPL_EA', type='number', startIndex=104, endIndex=106,
                    required=True, validators=[]),
              Field(item=51, name='ED_NO_HIGH_SCHOOL_DIPL_HOL', type='number', startIndex=106, endIndex=108,
                    required=True, validators=[]),
              Field(item=52, name='SCHOOL_ATTENDENCE_HOP', type='number', startIndex=108, endIndex=110,
                    required=True, validators=[]),
              Field(item=53, name='SCHOOL_ATTENDENCE_EA', type='number', startIndex=110, endIndex=112,
                    required=True, validators=[]),
              Field(item=54, name='SCHOOL_ATTENDENCE_HOL', type='number', startIndex=112, endIndex=114,
                    required=True, validators=[]),
              Field(item=55, name='PROVIDE_CC_HOP', type='number', startIndex=114, endIndex=116,
                    required=True, validators=[]),
              Field(item=56, name='PROVIDE_CC_EA', type='number', startIndex=116, endIndex=118,
                    required=True, validators=[]),
              Field(item=57, name='PROVIDE_CC_HOL', type='number', startIndex=118, endIndex=120,
                    required=True, validators=[]),
              Field(item=58, name='OTHER_WORK_ACTIVITIES', type='number', startIndex=120, endIndex=122,
                    required=True, validators=[]),
              Field(item=59, name='DEEMED_HOURS_FOR_OVERALL', type='number', startIndex=122, endIndex=124,
                    required=True, validators=[]),
              Field(item=60, name='DEEMED_HOURS_FOR_TWO_PARENT', type='number', startIndex=124, endIndex=126,
                    required=True, validators=[]),
              Field(item=61, name='EARNED_INCOME', type='number', startIndex=126, endIndex=130,
                    required=True, validators=[]),
              Field(item=62, name='UNEARNED_INCOME_TAX_CREDIT', type='number', startIndex=130, endIndex=134,
                    required=True, validators=[]),
              Field(item=63, name='UNEARNED_SOCIAL_SECURITY', type='number', startIndex=134, endIndex=138,
                    required=True, validators=[]),
              Field(item=64, name='UNEARNED_SSI', type='number', startIndex=138, endIndex=142,
                    required=True, validators=[]),
              Field(item=65, name='UNEARNED_WORKERS_COMP', type='number', startIndex=142, endIndex=146,
                    required=True, validators=[]),
              Field(item=66, name='OTHER_UNEARNED_INCOME', type='number', startIndex=146, endIndex=150,
                    required=True, validators=[]),
          ],
        )
      ]
  )
