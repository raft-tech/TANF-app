"""Schema for Tribal TANF T5 row of all submission types."""


from ...transforms import tanf_ssn_decryption_func
from ...fields import TransformField, Field
from ...row_schema import RowSchema, SchemaManager
from ... import validators
from tdpservice.search_indexes.documents.tribal import Tribal_TANF_T5DataSubmissionDocument


t5 = SchemaManager(
    schemas=[
        RowSchema(
            document=Tribal_TANF_T5DataSubmissionDocument(),
            preparsing_validators=[
                validators.hasLength(71),
                validators.or_priority_validators([
                    validators.field_year_month_with_header_year_quarter(),
                    validators.validateRptMonthYear(),
                ]),
                validators.notEmpty(8, 19)
            ],
            postparsing_validators=[
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.matches(1),
                    result_field="SSN",
                    result_function=validators.validateSSN(),
                ),
                validators.validate__FAM_AFF__SSN(),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field="RACE_HISPANIC",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field="RACE_AMER_INDIAN",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field="RACE_ASIAN",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field="RACE_BLACK",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field="RACE_HAWAIIAN",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field="RACE_WHITE",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field="MARITAL_STATUS",
                    result_function=validators.isInLimits(1, 5),
                ),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 2),
                    result_field="PARENT_MINOR_CHILD",
                    result_function=validators.isInLimits(1, 3),
                ),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.isInLimits(1, 3),
                    result_field="EDUCATION_LEVEL",
                    result_function=validators.or_validators(
                        validators.isInStringRange(1, 16),
                        validators.isInStringRange(98, 99),
                    ),
                ),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.matches(1),
                    result_field="CITIZENSHIP_STATUS",
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.validate__FAM_AFF__HOH__Count_Fed_Time(),
                validators.if_then_validator(
                    condition_field="FAMILY_AFFILIATION",
                    condition_function=validators.matches(1),
                    result_field="REC_FEDERAL_DISABILITY",
                    result_function=validators.isInLimits(1, 2),
                ),
            ],
            fields=[
                Field(
                    item="0",
                    name="RecordType",
                    friendly_name="Record Type",
                    type="string",
                    startIndex=0,
                    endIndex=2,
                    required=True,
                    validators=[],
                ),
                Field(
                    item="4",
                    name="RPT_MONTH_YEAR",
                    friendly_name="Reporting Year and Month",
                    type="number",
                    startIndex=2,
                    endIndex=8,
                    required=True,
                    validators=[
                        validators.dateYearIsLargerThan(1998),
                        validators.dateMonthIsValid(),
                    ],
                ),
                Field(
                    item="6",
                    name="CASE_NUMBER",
                    friendly_name="Case Number--TANF",
                    type="string",
                    startIndex=8,
                    endIndex=19,
                    required=True,
                    validators=[validators.notEmpty()],
                ),
                Field(
                    item="14",
                    name="FAMILY_AFFILIATION",
                    friendly_name="Family Affiliation",
                    type="number",
                    startIndex=19,
                    endIndex=20,
                    required=True,
                    validators=[validators.isInLimits(1, 5)],
                ),
                Field(
                    item="15",
                    name="DATE_OF_BIRTH",
                    friendly_name="Date of Birth",
                    type="string",
                    startIndex=20,
                    endIndex=28,
                    required=True,
                    validators=[validators.intHasLength(8),
                                validators.dateYearIsLargerThan(1900),
                                validators.dateMonthIsValid(),
                                validators.dateDayIsValid()
                                ]
                ),
                TransformField(
                    transform_func=tanf_ssn_decryption_func,
                    item="16",
                    name="SSN",
                    friendly_name="Social Security Number",
                    type="string",
                    startIndex=28,
                    endIndex=37,
                    required=True,
                    validators=[validators.isNumber()],
                    is_encrypted=False,
                ),
                Field(
                    item="17A",
                    name="RACE_HISPANIC",
                    friendly_name="Ethnicity/Race: Hispanic or Latino",
                    type="number",
                    startIndex=37,
                    endIndex=38,
                    required=False,
                    validators=[validators.validateRace()],
                ),
                Field(
                    item="17B",
                    name="RACE_AMER_INDIAN",
                    friendly_name="Ethnicity/Race: American Indian or Alaska Native",
                    type="number",
                    startIndex=38,
                    endIndex=39,
                    required=False,
                    validators=[validators.validateRace()],
                ),
                Field(
                    item="17C",
                    name="RACE_ASIAN",
                    friendly_name="Ethnicity/Race: Asian",
                    type="number",
                    startIndex=39,
                    endIndex=40,
                    required=False,
                    validators=[validators.validateRace()],
                ),
                Field(
                    item="17D",
                    name="RACE_BLACK",
                    friendly_name="Ethnicity/Race: Black or African American",
                    type="number",
                    startIndex=40,
                    endIndex=41,
                    required=False,
                    validators=[validators.validateRace()],
                ),
                Field(
                    item="17E",
                    name="RACE_HAWAIIAN",
                    friendly_name="Ethnicity/Race: Hawaiian or Other Pacific Islander",
                    type="number",
                    startIndex=41,
                    endIndex=42,
                    required=False,
                    validators=[validators.validateRace()],
                ),
                Field(
                    item="17F",
                    name="RACE_WHITE",
                    friendly_name="Ethnicity/Race: White",
                    type="number",
                    startIndex=42,
                    endIndex=43,
                    required=False,
                    validators=[validators.validateRace()],
                ),
                Field(
                    item="18",
                    name="GENDER",
                    friendly_name="Gender",
                    type="number",
                    startIndex=43,
                    endIndex=44,
                    required=False,
                    validators=[validators.isInLimits(0, 9)],
                ),
                Field(
                    item="19A",
                    name="REC_OASDI_INSURANCE",
                    friendly_name="Receives Disability Benefits: OASDI Program",
                    type="number",
                    startIndex=44,
                    endIndex=45,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="19B",
                    name="REC_FEDERAL_DISABILITY",
                    friendly_name="Received Disability Benefits: Federal Disability Status",
                    type="number",
                    startIndex=45,
                    endIndex=46,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="19C",
                    name="REC_AID_TOTALLY_DISABLED",
                    friendly_name="Received Disability Benefits: Permanently and Totally Disabled Under Title XIV-APDT",
                    type="number",
                    startIndex=46,
                    endIndex=47,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="19D",
                    name="REC_AID_AGED_BLIND",
                    friendly_name="Received Disability Benefits: Aged, Blind, and Disabled Under Title XVI-AABD",
                    type="number",
                    startIndex=47,
                    endIndex=48,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="19E",
                    name="REC_SSI",
                    friendly_name="Received Disability Benefits: Supplemental Security Income Under Title XVI-SSI",
                    type="number",
                    startIndex=48,
                    endIndex=49,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="20",
                    name="MARITAL_STATUS",
                    friendly_name="Marital Status",
                    type="number",
                    startIndex=49,
                    endIndex=50,
                    required=False,
                    validators=[validators.isInLimits(0, 5)],
                ),
                Field(
                    item="21",
                    name="RELATIONSHIP_HOH",
                    friendly_name="Relationship to Head-of-Household",
                    type="string",
                    startIndex=50,
                    endIndex=52,
                    required=True,
                    validators=[validators.isInStringRange(1, 10)],
                ),
                Field(
                    item="22",
                    name="PARENT_MINOR_CHILD",
                    friendly_name="Parent With Minor Child in the Family",
                    type="number",
                    startIndex=52,
                    endIndex=53,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="23",
                    name="NEEDS_OF_PREGNANT_WOMAN",
                    friendly_name="Needs of a Pregnant Woman",
                    type="number",
                    startIndex=53,
                    endIndex=54,
                    required=False,
                    validators=[validators.isInLimits(0, 2)],
                ),
                Field(
                    item="24",
                    name="EDUCATION_LEVEL",
                    friendly_name="Educational Level",
                    type="string",
                    startIndex=54,
                    endIndex=56,
                    required=False,
                    validators=[
                        validators.or_validators(
                            validators.isInStringRange(0, 16),
                            validators.isInStringRange(98, 99),
                        )
                    ],
                ),
                Field(
                    item="25",
                    name="CITIZENSHIP_STATUS",
                    friendly_name="Citizenship/Alienage",
                    type="number",
                    startIndex=56,
                    endIndex=57,
                    required=False,
                    validators=[
                        validators.or_validators(
                            validators.isInLimits(0, 2), validators.matches(9)
                        )
                    ],
                ),
                Field(
                    item="26",
                    name="COUNTABLE_MONTH_FED_TIME",
                    friendly_name="Number of Months Countable toward Tribal Time Limit:",
                    type="string",
                    startIndex=57,
                    endIndex=60,
                    required=False,
                    validators=[validators.isInStringRange(0, 999)],
                ),
                Field(
                    item="27",
                    name="COUNTABLE_MONTHS_STATE_TRIBE",
                    friendly_name="Number of Countable Months Remaining Under Tribe's Time Limit",
                    type="string",
                    startIndex=60,
                    endIndex=62,
                    required=False,
                    validators=[validators.isInStringRange(0, 99)],
                ),
                Field(
                    item="28",
                    name="EMPLOYMENT_STATUS",
                    friendly_name="Employment Status",
                    type="number",
                    startIndex=62,
                    endIndex=63,
                    required=False,
                    validators=[validators.isInLimits(0, 3)],
                ),
                Field(
                    item="29",
                    name="AMOUNT_EARNED_INCOME",
                    friendly_name="Amount of Earned Income",
                    type="string",
                    startIndex=63,
                    endIndex=67,
                    required=True,
                    validators=[validators.isInStringRange(0, 9999)],
                ),
                Field(
                    item="30",
                    name="AMOUNT_UNEARNED_INCOME",
                    friendly_name="Amount of Unearned Income",
                    type="string",
                    startIndex=67,
                    endIndex=71,
                    required=True,
                    validators=[validators.isInStringRange(0, 9999)],
                ),
            ],
        )
    ]
)
