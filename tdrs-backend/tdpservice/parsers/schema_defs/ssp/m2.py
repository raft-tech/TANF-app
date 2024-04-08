"""Schema for SSP M1 record type."""


from tdpservice.parsers.transforms import ssp_ssn_decryption_func
from tdpservice.parsers.fields import TransformField, Field
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers import validators
from tdpservice.search_indexes.documents.ssp import SSP_M2DataSubmissionDocument


m2 = SchemaManager(
    schemas=[
        RowSchema(
            record_type="M2",
            document=SSP_M2DataSubmissionDocument(),
            preparsing_validators=[
                validators.recordHasLength(150),
                validators.caseNumberNotEmpty(8, 19),
                validators.or_priority_validators([
                    validators.field_year_month_with_header_year_quarter(),
                    validators.validateRptMonthYear(),
                ]),
            ],
            postparsing_validators=[
                validators.validate__FAM_AFF__SSN(),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.matches(1),
                    result_field_name='SSN',
                    result_function=validators.validateSSN(),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='RACE_HISPANIC',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='RACE_AMER_INDIAN',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='RACE_ASIAN',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='RACE_BLACK',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='RACE_HAWAIIAN',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='RACE_WHITE',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='MARITAL_STATUS',
                    result_function=validators.isInLimits(1, 5),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 2),
                    result_field_name='PARENT_MINOR_CHILD',
                    result_function=validators.isInLimits(1, 3),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='EDUCATION_LEVEL',
                    result_function=validators.or_validators(
                        validators.isInStringRange(1, 16),
                        validators.isInStringRange(98, 99),
                    ),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.matches(1),
                    result_field_name='CITIZENSHIP_STATUS',
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='COOPERATION_CHILD_SUPPORT',
                    result_function=validators.oneOf((1, 2, 9)),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field_name='EMPLOYMENT_STATUS',
                    result_function=validators.isInLimits(1, 3),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.oneOf((1, 2)),
                    result_field_name='WORK_ELIGIBLE_INDICATOR',
                    result_function=validators.or_validators(
                        validators.isInLimits(1, 9),
                        validators.oneOf((11, 12))
                    ),
                ),
                validators.if_then_validator(
                    condition_field_name='FAMILY_AFFILIATION',
                    condition_function=validators.oneOf((1, 2)),
                    result_field_name='WORK_PART_STATUS',
                    result_function=validators.oneOf([1, 2, 5, 7, 9, 15, 16, 17, 18, 99]),
                ),
                validators.if_then_validator(
                    condition_field_name='WORK_ELIGIBLE_INDICATOR',
                    condition_function=validators.isInLimits(1, 5),
                    result_field_name='WORK_PART_STATUS',
                    result_function=validators.notMatches(99),
                ),
            ],
            fields=[
                Field(
                    item="0",
                    name='RecordType',
                    friendly_name="Record Type",
                    type='string',
                    startIndex=0,
                    endIndex=2,
                    required=True,
                    validators=[]
                ),
                Field(
                    item="3",
                    name='RPT_MONTH_YEAR',
                    friendly_name="Reporting Year and Month",
                    type='number',
                    startIndex=2,
                    endIndex=8,
                    required=True,
                    validators=[
                        validators.dateYearIsLargerThan(1998),
                        validators.dateMonthIsValid(),
                    ]
                ),
                Field(
                    item="5",
                    name='CASE_NUMBER',
                    friendly_name="Case Number",
                    type='string',
                    startIndex=8,
                    endIndex=19,
                    required=True,
                    validators=[validators.notEmpty()]
                ),
                Field(
                    item="26",
                    name='FAMILY_AFFILIATION',
                    friendly_name="Family Affiliation",
                    type='number',
                    startIndex=19,
                    endIndex=20,
                    required=True,
                    validators=[validators.oneOf([1, 2, 3, 5])]
                ),
                Field(
                    item="27",
                    name='NONCUSTODIAL_PARENT',
                    friendly_name="Noncustodial Parent Indicator",
                    type='number',
                    startIndex=20,
                    endIndex=21,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="28",
                    name='DATE_OF_BIRTH',
                    friendly_name="Date of Birth",
                    type='string',
                    startIndex=21,
                    endIndex=29,
                    required=True,
                    validators=[validators.isLargerThan(0)]
                ),
                TransformField(
                    transform_func=ssp_ssn_decryption_func,
                    item="29",
                    name='SSN',
                    friendly_name="Social Security Number",
                    type='string',
                    startIndex=29,
                    endIndex=38,
                    required=True,
                    validators=[validators.isNumber()],
                    is_encrypted=False
                ),
                Field(
                    item="30A",
                    name='RACE_HISPANIC',
                    type='number',
                    friendly_name="Race/Ethnicity: Hispanic or Latino",
                    startIndex=38,
                    endIndex=39,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30B",
                    name='RACE_AMER_INDIAN',
                    friendly_name="Race/Ethnicity: American Indian or Alaska Native",
                    type='number',
                    startIndex=39,
                    endIndex=40,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30C",
                    name='RACE_ASIAN',
                    friendly_name="Race/Ethnicity: Asian",
                    type='number',
                    startIndex=40,
                    endIndex=41,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30D",
                    name='RACE_BLACK',
                    friendly_name="Race/Ethnicity: Black or African American",
                    type='number',
                    startIndex=41,
                    endIndex=42,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30E",
                    name='RACE_HAWAIIAN',
                    friendly_name="Race/Ethnicity: Native Hawaiian or Other Pacific Islander",
                    type='number',
                    startIndex=42,
                    endIndex=43,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30F",
                    name='RACE_WHITE',
                    friendly_name="Race/Ethnicity: White",
                    type='number',
                    startIndex=43,
                    endIndex=44,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="31",
                    name='GENDER',
                    friendly_name="Gender",
                    type='number',
                    startIndex=44,
                    endIndex=45,
                    required=True,
                    validators=[validators.isLargerThanOrEqualTo(0)]
                ),
                Field(
                    item="32A",
                    name='FED_OASDI_PROGRAM',
                    friendly_name="Receives Disability Benefits: OASDI Program",
                    type='number',
                    startIndex=45,
                    endIndex=46,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="32B",
                    name='FED_DISABILITY_STATUS',
                    friendly_name="Receives Disability Benefits: Federal Disability Status",
                    type='number',
                    startIndex=46,
                    endIndex=47,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="32C",
                    name='DISABLED_TITLE_XIVAPDT',
                    friendly_name="Receives Disability Benefits: Permanently and Totally Disabled Under Title XIV-APDT",
                    type='number',
                    startIndex=47,
                    endIndex=48,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="32D",
                    name='AID_AGED_BLIND',
                    friendly_name="Receives Disability Benefits: Code no longer in use.",
                    type='number',
                    startIndex=48,
                    endIndex=49,
                    required=False,
                    validators=[validators.isLargerThanOrEqualTo(0)]
                ),
                Field(
                    item="32E",
                    name='RECEIVE_SSI',
                    friendly_name="Receives Disability Benefits: Supplemental Security Income Under Title XVI-SSI ",
                    type='number',
                    startIndex=49,
                    endIndex=50,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="33",
                    name='MARITAL_STATUS',
                    friendly_name="Marital Status",
                    type='number',
                    startIndex=50,
                    endIndex=51,
                    required=False,
                    validators=[validators.isInLimits(0, 5)]
                ),
                Field(
                    item="34",
                    name='RELATIONSHIP_HOH',
                    friendly_name="Relationship to Head-of-Household",
                    type='string',
                    startIndex=51,
                    endIndex=53,
                    required=True,
                    validators=[validators.isInStringRange(1, 10)]
                ),
                Field(
                    item="35",
                    name='PARENT_MINOR_CHILD',
                    friendly_name="Parent with Minor Child in the Family",
                    type='number',
                    startIndex=53,
                    endIndex=54,
                    required=False,
                    validators=[validators.isInLimits(0, 3)]
                ),
                Field(
                    item="36",
                    name='NEEDS_PREGNANT_WOMAN',
                    friendly_name="Needs of a Pregnant Woman",
                    type='number',
                    startIndex=54,
                    endIndex=55,
                    required=False,
                    validators=[validators.isInLimits(0, 9)]
                ),
                Field(
                    item="37",
                    name='EDUCATION_LEVEL',
                    friendly_name="Educational Level",
                    type='number',
                    startIndex=55,
                    endIndex=57,
                    required=False,
                    validators=[
                        validators.or_validators(
                            validators.isInLimits(0, 16), validators.isInLimits(98, 99)
                        )
                    ]
                ),
                Field(
                    item="38",
                    name='CITIZENSHIP_STATUS',
                    friendly_name="Citizenship/Immigration Status",
                    type='number',
                    startIndex=57,
                    endIndex=58,
                    required=False,
                    validators=[validators.oneOf([0, 1, 2, 3, 9])]
                ),
                Field(
                    item="39",
                    name='COOPERATION_CHILD_SUPPORT',
                    friendly_name="Cooperated with Child Support",
                    type='number',
                    startIndex=58,
                    endIndex=59,
                    required=False,
                    validators=[validators.oneOf([0, 1, 2, 9])]
                ),
                Field(
                    item="40",
                    name='EMPLOYMENT_STATUS',
                    friendly_name="Employment Status",
                    type='number',
                    startIndex=59,
                    endIndex=60,
                    required=False,
                    validators=[validators.isInLimits(0, 3)]
                ),
                Field(
                    item="41",
                    name='WORK_ELIGIBLE_INDICATOR',
                    friendly_name="Work-Eligible Individual Indicator",
                    type='number',
                    startIndex=60,
                    endIndex=62,
                    required=True,
                    validators=[
                        validators.or_validators(
                            validators.isInLimits(1, 4),
                            validators.isInLimits(6, 9),
                            validators.isInLimits(11, 12),
                        )
                    ]
                ),
                Field(
                    item="42",
                    name='WORK_PART_STATUS',
                    friendly_name="Work Participation Status",
                    type='number',
                    startIndex=62,
                    endIndex=64,
                    required=False,
                    validators=[validators.oneOf([1, 2, 5, 7, 9, 15, 16, 17, 18, 19, 99])]
                ),
                Field(
                    item="43",
                    name='UNSUB_EMPLOYMENT',
                    friendly_name="Unsubsidized Employment",
                    type='number',
                    startIndex=64,
                    endIndex=66,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="44",
                    name='SUB_PRIVATE_EMPLOYMENT',
                    friendly_name="Subsidized Private-Sector Employment",
                    type='number',
                    startIndex=66,
                    endIndex=68,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="45",
                    name='SUB_PUBLIC_EMPLOYMENT',
                    friendly_name="Subsidized Public-Sector Employment",
                    type='number',
                    startIndex=68,
                    endIndex=70,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="46A",
                    name='WORK_EXPERIENCE_HOP',
                    friendly_name="Work Experience: Hours of Participation",
                    type='number',
                    startIndex=70,
                    endIndex=72,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="46B",
                    name='WORK_EXPERIENCE_EA',
                    friendly_name="Work Experience: Hours of Excused Absences",
                    type='number',
                    startIndex=72,
                    endIndex=74,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="46C",
                    name='WORK_EXPERIENCE_HOL',
                    friendly_name="Work Experience: Hours of Holidays",
                    type='number',
                    startIndex=74,
                    endIndex=76,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="47",
                    name='OJT',
                    friendly_name="On-the-job Training ",
                    type='number',
                    startIndex=76,
                    endIndex=78,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="48A",
                    name='JOB_SEARCH_HOP',
                    friendly_name="Job Search and Job Readiness Assistance: Hours of Participation",
                    type='number',
                    startIndex=78,
                    endIndex=80,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="48B",
                    name='JOB_SEARCH_EA',
                    friendly_name="Job Search and Job Readiness Assistance: Hours of Excused Absences",
                    type='number',
                    startIndex=80,
                    endIndex=82,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="48C",
                    name='JOB_SEARCH_HOL',
                    friendly_name="Job Search and Job Readiness Assistance: Hours of Holidays",
                    type='number',
                    startIndex=82,
                    endIndex=84,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="49A",
                    name='COMM_SERVICES_HOP',
                    friendly_name="Community Service Program: Hours of Participation",
                    type='number',
                    startIndex=84,
                    endIndex=86,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="49B",
                    name='COMM_SERVICES_EA',
                    friendly_name="Community Service Program: Hours of Excused Absences",
                    type='number',
                    startIndex=86,
                    endIndex=88,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="49C",
                    name='COMM_SERVICES_HOL',
                    friendly_name="Community Service Program: Hours of Holidays",
                    type='number',
                    startIndex=88,
                    endIndex=90,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="50A",
                    name='VOCATIONAL_ED_TRAINING_HOP',
                    friendly_name="Vocational Educational Training: Hours of Participation",
                    type='number',
                    startIndex=90,
                    endIndex=92,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="50B",
                    name='VOCATIONAL_ED_TRAINING_EA',
                    friendly_name="Vocational Educational Training: Hours of Excused Absences",
                    type='number',
                    startIndex=92,
                    endIndex=94,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="50C",
                    name='VOCATIONAL_ED_TRAINING_HOL',
                    friendly_name="Vocational Educational Training: Hours of Holidays",
                    type='number',
                    startIndex=94,
                    endIndex=96,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="51A",
                    name='JOB_SKILLS_TRAINING_HOP',
                    friendly_name="Job Skills Training: Hours of Participation",
                    type='number',
                    startIndex=96,
                    endIndex=98,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="51B",
                    name='JOB_SKILLS_TRAINING_EA',
                    friendly_name="Job Skills Training: Hours of Excused Absences",
                    type='number',
                    startIndex=98,
                    endIndex=100,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="51C",
                    name='JOB_SKILLS_TRAINING_HOL',
                    friendly_name="Job Skills Training: Hours of Holidays",
                    type='number',
                    startIndex=100,
                    endIndex=102,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="52A",
                    name='ED_NO_HIGH_SCHOOL_DIPL_HOP',
                    friendly_name="Education Directly Related to Employment for an Individual with NO High " +
                    "School Diploma or Certificate of High School Equivalency: Hours of Participation",
                    type='number',
                    startIndex=102,
                    endIndex=104,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="52B",
                    name='ED_NO_HIGH_SCHOOL_DIPL_EA',
                    friendly_name="Education Directly Related to Employment for an Individual with NO High " +
                    "School Diploma or Certificate of High School Equivalency: Hours of Excused Absences",
                    type='number',
                    startIndex=104,
                    endIndex=106,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="52C",
                    name='ED_NO_HIGH_SCHOOL_DIPL_HOL',
                    friendly_name="Education Directly Related to Employment for an Individual with NO High " +
                    "School Diploma or Certificate of High School Equivalency: Hours of Holidays",
                    type='number',
                    startIndex=106,
                    endIndex=108,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="53A",
                    name='SCHOOL_ATTENDENCE_HOP',
                    friendly_name="Satisfactory School Attendance for Individuals with No High School Diploma " +
                    "or Certificate of High School Equivalency: Hours of Participation",
                    type='number',
                    startIndex=108,
                    endIndex=110,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="53B",
                    name='SCHOOL_ATTENDENCE_EA',
                    friendly_name="Satisfactory School Attendance for Individuals with No High School Diploma or " +
                    "Certificate of High School Equivalency: Hours of Excused Absences",
                    type='number',
                    startIndex=110,
                    endIndex=112,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="53C",
                    name='SCHOOL_ATTENDENCE_HOL',
                    friendly_name="Satisfactory School Attendance for Individuals with No High School Diploma " +
                    "or Certificate: Hours of Holidays",
                    type='number',
                    startIndex=112,
                    endIndex=114,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="54A",
                    name='PROVIDE_CC_HOP',
                    friendly_name="Providing Child Care Services to an Individual Who Is Participating in a " +
                    "Community Service Program: Hours of Participation",
                    type='number',
                    startIndex=114,
                    endIndex=116,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="54B",
                    name='PROVIDE_CC_EA',
                    friendly_name="Providing Child Care Services to an Individual Who Is Participating in a " +
                    "Community Service Program: Hours of Excused Absences",
                    type='number',
                    startIndex=116,
                    endIndex=118,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="54C",
                    name='PROVIDE_CC_HOL',
                    friendly_name="Providing Child Care Services to an Individual Who Is Participating in a " +
                    "Community Service Program: Hours of Holidays",
                    type='number',
                    startIndex=118,
                    endIndex=120,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="55",
                    name='OTHER_WORK_ACTIVITIES',
                    friendly_name="Hours of Other Work Activities",
                    type='number',
                    startIndex=120,
                    endIndex=122,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="56",
                    name='DEEMED_HOURS_FOR_OVERALL',
                    friendly_name="Number of Deemed Core Hours for Overall Rate",
                    type='number',
                    startIndex=122,
                    endIndex=124,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="57",
                    name='DEEMED_HOURS_FOR_TWO_PARENT',
                    friendly_name="Number of Deemed Core Hours for the Two-Parent Rate",
                    type='number',
                    startIndex=124,
                    endIndex=126,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="58",
                    name='EARNED_INCOME',
                    friendly_name="Amount of Earned Income",
                    type='number',
                    startIndex=126,
                    endIndex=130,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59A",
                    name='UNEARNED_INCOME_TAX_CREDIT',
                    friendly_name="Amount of Unearned Income: Tax Credit",
                    type='number',
                    startIndex=130,
                    endIndex=134,
                    required=False,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59B",
                    name='UNEARNED_SOCIAL_SECURITY',
                    friendly_name="Amount of Unearned Income: Social Security",
                    type='number',
                    startIndex=134,
                    endIndex=138,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59C",
                    name='UNEARNED_SSI',
                    friendly_name="Amount of Unearned Income: Social Security: SSI Benefit",
                    type='number',
                    startIndex=138,
                    endIndex=142,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59D",
                    name='UNEARNED_WORKERS_COMP',
                    friendly_name="Amount of Unearned Income: Worker's Compensation",
                    type='number',
                    startIndex=142,
                    endIndex=146,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59E",
                    name='OTHER_UNEARNED_INCOME',
                    friendly_name="Amount of Unearned Income: Other",
                    type='number',
                    startIndex=146,
                    endIndex=150,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
            ],
        )
    ]
)
