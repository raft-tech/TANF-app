"""Schema for HEADER row of all submission types."""


from ...util import RowSchema, Field
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T2


t2 = RowSchema(
    model=TANF_T2,
    preparsing_validators=[
        validators.hasLength(156),
    ],
    postparsing_validators=[],
    fields=[
        Field(name='RecordType', type='string', startIndex=0, endIndex=2, required=True, validators=[
        ]),
        Field(name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8, required=True, validators=[
        ]),
        Field(name='CASE_NUMBER', type='string', startIndex=8, endIndex=19, required=True, validators=[
        ]),
        Field(name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20, required=True, validators=[
        ]),
        Field(name='NONCUSTODIAL_PARENT', type='number', startIndex=20, endIndex=21, required=True, validators=[
        ]),
        Field(name='DOB', type='number', startIndex=21, endIndex=29, required=True, validators=[
        ]),
        Field(name='SSN', type='string', startIndex=29, endIndex=38, required=True, validators=[
        ]),
        Field(name='RACE_HISPANIC_OR_LATINO', type='string', startIndex=38, endIndex=39, required=True, validators=[
        ]),
        Field(name='RACE_AMERICAN_INDIAN_OR_ALASKA_NATIVE', type='string', startIndex=39, endIndex=40,
              required=True, validators=[]),
        Field(name='RACE_ASIAN', type='string', startIndex=40, endIndex=41, required=True, validators=[
        ]),
        Field(name='RACE_BLACK_OR_AFRICAN_AMERICAN', type='string', startIndex=41, endIndex=42, required=True,
              validators=[]),
        Field(name='RACE_NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER', type='string', startIndex=42, endIndex=43,
              required=True, validators=[]),
        Field(name='RACE_WHITE', type='string', startIndex=43, endIndex=44, required=True, validators=[
        ]),
        Field(name='GENDER', type='number', startIndex=44, endIndex=45, required=True, validators=[
        ]),
        Field(name='RECEIVES_FEDERAL_DISABILITY_INSURANCE_OASDI_PROGRAM', type='string', startIndex=45,
              endIndex=46, required=True, validators=[]),
        Field(name='RECEIVES_BENEFITS_BASED_ON_FEDERAL_DISABILITY_STATUS', type='string', startIndex=46,
              endIndex=47, required=True, validators=[]),
        Field(name='RECEIVES_AID_TOTALLY_DISABLED_UNDER_TITLE_XIV_APDT', type='string',
              startIndex=47, endIndex=48, required=True, validators=[]),
        Field(name='RECEIVES_AID_TO_THE_AGED', type='string', startIndex=48, endIndex=49, required=True,
              validators=[]),
        Field(name='RECEIVES_SUPPLEMENTAL_SECURITY_INCOME_TITLE_XVI_SSI', type='string', startIndex=49,
              endIndex=50, required=True, validators=[]),
        Field(name='MARITAL_STATUS', type='string', startIndex=50, endIndex=51, required=True, validators=[
        ]),
        Field(name='RELATIONSHIP_TO_HEAD_OF_HOUSEHOLD', type='number', startIndex=51, endIndex=53, required=True,
              validators=[]),
        Field(name='PARENT_WITH_MINOR_CHILD', type='string', startIndex=53, endIndex=54, required=True, validators=[
        ]),
        Field(name='NEEDS_OF_A_PREGNANT_WOMAN', type='string', startIndex=54, endIndex=55, required=True, validators=[
        ]),
        Field(name='EDUCATION_LEVEL', type='string', startIndex=55, endIndex=57, required=True, validators=[
        ]),
        Field(name='CITIZENSHIP_STATUS', type='string', startIndex=57, endIndex=58, required=True, validators=[
        ]),
        Field(name='COOPERATION_WITH_CHILD_SUPPORT', type='string', startIndex=58, endIndex=59, required=True,
              validators=[]),
        Field(name='NUMBER_OF_COUNTABLE_MONTHS', type='string', startIndex=59, endIndex=62, required=True, validators=[
        ]),
        Field(name='NUMBER_OF_COUNTABLE_MONTHS_REMAINING', type='string', startIndex=62, endIndex=64, required=True,
              validators=[]),
        Field(name='CURRENT_MONTH_EXEMPT_FROM_STATE', type='string', startIndex=64, endIndex=65, required=True,
              validators=[]),
        Field(name='EMPLOYMENT_STATUS', type='string', startIndex=65, endIndex=66, required=True, validators=[
        ]),
        Field(name='WORK_ELIGIBLE_INDIVIDUAL_INDICATOR', type='string', startIndex=66, endIndex=68, required=True,
              validators=[]),
        Field(name='WORK_PARTICIPATION_STATUS', type='string', startIndex=68, endIndex=70, required=True, validators=[
        ]),
        Field(name='UNSUBSIDIZED_EMPLOYMENT', type='string', startIndex=70, endIndex=72, required=True, validators=[
        ]),
        Field(name='SUBSIDIZED_PRIVATE_EMPLOYMENT', type='string', startIndex=72, endIndex=74, required=True,
              validators=[]),
        Field(name='SUBSIDIZED_PUBLIC_EMPLOYMENT', type='string', startIndex=74, endIndex=76, required=True,
              validators=[]),
        Field(name='WORK_EXP_HOURS_OF_PARTICIPATION', type='string', startIndex=76, endIndex=78, required=True,
              validators=[]),
        Field(name='WORK_EXP_EXCUSED_ABSENCES', type='string', startIndex=78, endIndex=80, required=True, validators=[
        ]),
        Field(name='WORK_EXP_HOLIDAYS', type='string', startIndex=80, endIndex=82, required=True, validators=[
        ]),
        Field(name='ON_THE_JOB_TRAINING', type='string', startIndex=82, endIndex=84, required=True, validators=[
        ]),
        Field(name='JOB_SEARCH_HOURS_OF_PARTICIPATION', type='string', startIndex=84, endIndex=86, required=True,
              validators=[]),
        Field(name='JOB_SEARCH_EXCUSED_ABSENCES', type='string', startIndex=86, endIndex=88, required=True, validators=[
        ]),
        Field(name='JOB_SEARCH_HOLIDAYS', type='string', startIndex=88, endIndex=90, required=True, validators=[
        ]),
        Field(name='COMMUNITY_SVS_HOURS_OF_PARTICIPATION', type='string', startIndex=90, endIndex=92, required=True,
              validators=[]),
        Field(name='COMMUNITY_SVS_EXCUSED_ABSENCES', type='string', startIndex=92, endIndex=94, required=True, validators=[
        ]),
        Field(name='COMMUNITY_SVS_HOLIDAYS', type='string', startIndex=94, endIndex=96, required=True, validators=[
        ]),
        Field(name='VOCATIONAL_ED_HOURS_OF_PARTICIPATION', type='string', startIndex=96, endIndex=98, required=False,
              validators=[]),
        Field(name='VOCATIONAL_ED_EXCUSED_ABSENCES', type='string', startIndex=98, endIndex=100, required=False,
              validators=[]),
        Field(name='VOCATIONAL_ED_HOLIDAYS', type='string', startIndex=100, endIndex=102, required=False, validators=[]),
        Field(name='JOB_SKILLS_HOURS_OF_PARTICIPATION', type='string', startIndex=102, endIndex=104, required=False,
              validators=[]),
        Field(name='JOB_SKILLS_EXCUSED_ABSENCES', type='string', startIndex=104, endIndex=106, required=False,
              validators=[]),
        Field(name='JOB_SKILLS_HOLIDAYS', type='string', startIndex=106, endIndex=108, required=False, validators=[]),
        Field(name='EDUCATION_RELATED_HOURS_OF_PARTICIPATION', type='string', startIndex=108, endIndex=110, required=False,
              validators=[]),
        Field(name='EDUCATION_RELATED_EXCUSED_ABSENCES', type='string', startIndex=110, endIndex=112, required=False,
              validators=[]),
        Field(name='EDUCATION_RELATED_HOLIDAYS', type='string', startIndex=112, endIndex=114, required=False, validators=[]),
        Field(name='SCHOOL_ATTENDENCE_HOURS_OF_PARTICIPATION', type='string', startIndex=114, endIndex=116, required=False,
              validators=[]),
        Field(name='SCHOOL_ATTENDENCE_EXCUSED_ABSENCES', type='string', startIndex=116, endIndex=118, required=False,
              validators=[]),
        Field(name='SCHOOL_ATTENDENCE_HOLIDAYS', type='string', startIndex=118, endIndex=120, required=False, validators=[]),
        Field(name='CHILD_CARE_HOURS_OF_PARTICIPATION', type='string', startIndex=120, endIndex=122, required=False,
              validators=[]),
        Field(name='CHILD_CARE_EXCUSED_ABSENCES', type='string', startIndex=122, endIndex=124, required=False,
              validators=[]),
        Field(name='CHILD_CARE_HOLIDAYS', type='string', startIndex=124, endIndex=126, required=False, validators=[]),
        Field(name='OTHER_WORK_ACTIVITIES', type='string', startIndex=126, endIndex=128, required=False, validators=[]),
        Field(name='NUMBER_OF_DEEMED_CORE_HOURS_FOR_OVERALL_RATE', type='string', startIndex=128, endIndex=130,
              required=False, validators=[]),
        Field(name='NUMBER_OF_DEEMED_CORE_HOURS_FOR_TWO_PARENT_RATE', type='string', startIndex=130, endIndex=132,
              required=False, validators=[]),
        Field(name='AMOUNT_OF_EARNED_INCOME', type='string', startIndex=132, endIndex=136, required=False,
              validators=[]),
        Field(name='UNEARNED_INCOME_EARNED_INCOME_TAX_CREDIT', type='string', startIndex=136, endIndex=140, required=False,
              validators=[]),
        Field(name='UNEARNED_INCOME_SOCIAL_SECURITY', type='string', startIndex=140, endIndex=144, required=False,
              validators=[]),
        Field(name='UNEARNED_INCOME_SSI', type='string', startIndex=144, endIndex=148, required=False, validators=[]),
        Field(name='UNEARNED_INCOME_WORKERS_COMPENSATION', type='string', startIndex=148, endIndex=152, required=False,
              validators=[]),
        Field(name='UNEARNED_INCOME_OTHER_UNEARNED_INCOME', type='string', startIndex=152, endIndex=156, required=False,
              validators=[]),
    ],
)
