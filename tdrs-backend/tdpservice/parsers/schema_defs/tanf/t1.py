"""Schema for HEADER row of all submission types."""

from ..cat3_validators import cat3_validate_t1
from ...util import RowSchema, Field
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T1


t1 = RowSchema(
    model=TANF_T1,
    preparsing_validators=[
        validators.hasLength(156),
    ],
    postparsing_validators=[
      cat3_validate_t1,
      validators.if_then_validator(
            condition_field='DISPOSITION', condition_function=validators.matches(2), 
            result_field='COUNTY_FIPS_CODE', result_function=validators.notEmpty(),
      ),
      validators.if_then_validator(
            condition_field='DISPOSITION', condition_function=validators.matches(2), 
            result_field='REPORTING_MONTH', result_function=validators.notEmpty(),
      ),
      validators.if_then_validator(
            condition_field='DISPOSITION', condition_function=validators.matches(2), 
            result_field='STRATUM', result_function=validators.notEmpty(),
      ),
      validators.if_then_validator(
            condition_field='DISPOSITION', condition_function=validators.matches(2), 
            result_field='CASE_NUMBER', result_function=validators.notEmpty(),
      ),
      validators.if_then_validator(
            condition_field='CASH_AMOUNT', condition_function=validators.isLargerThan(0),
            result_field='NBR_MONTHS', result_function=validators.isLargerThan(0),
      ),
      validators.if_then_validator(
            condition_field='CC_AMOUNT', condition_function=validators.isLargerThan(0),
            result_field='CC_NBR_MONTHS', result_function=validators.isLargerThan(0),
      ),
      validators.if_then_validator(
          condition_field='CC_AMOUNT', condition_function=validators.isLargerThan(0),
          result_field='CHILDREN_COVERED', result_function=validators.isLargerThan(0),
      )
      ],
    fields=[
        Field(item=1, name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item=2, name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              required=True, validators=[
                  validators.month_year_yearIsLargerThan(1998),
                  validators.month_year_monthIsValid(),
              ]),
        Field(item=3, name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              required=True, validators=[
                  validators.notEmpty(),
              ]),
        Field(item=4, name='COUNTY_FIPS_CODE', type='string', startIndex=19, endIndex=22,
              required=True, validators=[
                  validators.oneOf(
                        [
                              '01', '02',
                              '04', '05', '06',
                              '08', '09', '10', '11', '12', '13',
                              '15', '16', '17', '18', '19', '20',
                              '21', '22', '23', '24', '25', '26',
                              '27', '28', '29', '30', '31', '32',
                              '33', '34', '35', '36', '37', '38',
                              '39', '40', '41', '42',
                              '44', '45', '46', '47', '48', '49', '50', '51',
                              '53', '54', '55', '56',
                              '60',
                              '66',
                              '72',
                              '78',
                        ],
                  ),
                  validators.isNumber(),
              ]),
        Field(item=5, name='STRATUM', type='number', startIndex=22, endIndex=24,
              required=True, validators=[
                  validators.isInLimits(0, 99),
              ]),
        Field(item=6, name='ZIP_CODE', type='string', startIndex=24, endIndex=29,
              required=True, validators=[
                  validators.isNumber(),
              ]),
        Field(item=7, name='FUNDING_STREAM', type='number', startIndex=29, endIndex=30,
              required=True, validators=[
                  validators.oneOf([1, 2]),
              ]),
        Field(item=8, name='DISPOSITION', type='number', startIndex=30, endIndex=31,
              required=True, validators=[
                  validators.oneOf([1, 2]),
              ]),
        Field(item=9, name='NEW_APPLICANT', type='number', startIndex=31, endIndex=32,
              required=True, validators=[]),
        Field(item=10, name='NBR_FAMILY_MEMBERS', type='number', startIndex=32, endIndex=34,
              required=True, validators=[
                  validators.isLargerThan(0),
              ]),
        Field(item=11, name='FAMILY_TYPE', type='number', startIndex=34, endIndex=35,
              required=True, validators=[
                  validators.isInLimits(1, 3),
              ]),
        Field(item=12, name='RECEIVES_SUB_HOUSING', type='number', startIndex=35, endIndex=36,
              required=True, validators=[
                  validators.isInLimits(1, 3),
              ]),
        Field(item=13, name='RECEIVES_MED_ASSISTANCE', type='number', startIndex=36, endIndex=37,
              required=True, validators=[
                  validators.isInLimits(1, 2),
              ]),
        Field(item=14, name='RECEIVES_FOOD_STAMPS', type='number', startIndex=37, endIndex=38,
              required=True, validators=[
                  validators.isInLimits(1, 2),
              ]),
        Field(item=15, name='AMT_FOOD_STAMP_ASSISTANCE', type='number', startIndex=38, endIndex=42,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item=16, name='RECEIVES_SUB_CC', type='number', startIndex=42, endIndex=43,
              required=True, validators=[
                  validators.isInLimits(1, 3),
              ]),
        Field(item=17, name='AMT_SUB_CC', type='number', startIndex=43, endIndex=47,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item=18, name='CHILD_SUPPORT_AMT', type='number', startIndex=47, endIndex=51,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item=19, name='FAMILY_CASH_RESOURCES', type='number', startIndex=51, endIndex=55,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item=20, name='CASH_AMOUNT', type='number', startIndex=55, endIndex=59,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item=21, name='NBR_MONTHS', type='number', startIndex=59, endIndex=62,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item=22, name='CC_AMOUNT', type='number', startIndex=62, endIndex=66,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item=23, name='CHILDREN_COVERED', type='number', startIndex=66, endIndex=68,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item=24, name='CC_NBR_MONTHS', type='number', startIndex=68, endIndex=71,
              required=True, validators=[
                  validators.isLargerThanOrEqualTo(0),
              ]),
        Field(item=25, name='TRANSP_AMOUNT', type='number', startIndex=71, endIndex=75,
              required=True, validators=[]),
        Field(item=26, name='TRANSP_NBR_MONTHS', type='number', startIndex=75, endIndex=78,
              required=True, validators=[]),
        Field(item=27, name='TRANSITION_SERVICES_AMOUNT', type='number', startIndex=78, endIndex=82,
              required=True, validators=[]),
        Field(item=28, name='TRANSITION_NBR_MONTHS', type='number', startIndex=82, endIndex=85,
              required=True, validators=[]),
        Field(item=29, name='OTHER_AMOUNT', type='number', startIndex=85, endIndex=89,
              required=True, validators=[]),
        Field(item=30, name='OTHER_NBR_MONTHS', type='number', startIndex=89, endIndex=92,
              required=True, validators=[]),
        Field(item=31, name='SANC_REDUCTION_AMT', type='number', startIndex=92, endIndex=96,
              required=True, validators=[]),
        Field(item=32, name='WORK_REQ_SANCTION', type='number', startIndex=96, endIndex=97,
              required=True, validators=[]),
        Field(item=33, name='FAMILY_SANC_ADULT', type='number', startIndex=97, endIndex=98,
              required=True, validators=[]),
        Field(item=34, name='SANC_TEEN_PARENT', type='number', startIndex=98, endIndex=99,
              required=True, validators=[]),
        Field(item=35, name='NON_COOPERATION_CSE', type='number', startIndex=99, endIndex=100,
              required=True, validators=[]),
        Field(item=36, name='FAILURE_TO_COMPLY', type='number', startIndex=100, endIndex=101,
              required=True, validators=[]),
        Field(item=37, name='OTHER_SANCTION', type='number', startIndex=101, endIndex=102,
              required=True, validators=[]),
        Field(item=38, name='RECOUPMENT_PRIOR_OVRPMT', type='number', startIndex=102, endIndex=106,
              required=True, validators=[]),
        Field(item=39, name='OTHER_TOTAL_REDUCTIONS', type='number', startIndex=106, endIndex=110,
              required=True, validators=[]),
        Field(item=40, name='FAMILY_CAP', type='number', startIndex=110, endIndex=111,
              required=True, validators=[]),
        Field(item=41, name='REDUCTIONS_ON_RECEIPTS', type='number', startIndex=111, endIndex=112,
              required=True, validators=[]),
        Field(item=42, name='OTHER_NON_SANCTION', type='number', startIndex=112, endIndex=113,
              required=True, validators=[]),
        Field(item=43, name='WAIVER_EVAL_CONTROL_GRPS', type='number', startIndex=113, endIndex=114,
              required=True, validators=[]),
        Field(item=44, name='FAMILY_EXEMPT_TIME_LIMITS', type='number', startIndex=114, endIndex=116,
              required=True, validators=[]),
        Field(item=45, name='FAMILY_NEW_CHILD', type='number', startIndex=116, endIndex=117,
              required=True, validators=[]),
        Field(item=46, name='BLANK', type='string', startIndex=117, endIndex=156, required=False, validators=[]),
    ],
)
