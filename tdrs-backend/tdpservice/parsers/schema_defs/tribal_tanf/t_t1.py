"""Schema for Tribal TANF T1 record types."""

from ...util import SchemaManager
from ...fields import Field
from ...row_schema import RowSchema
from ... import validators
from tdpservice.search_indexes.models.tribal import Tribal_TANF_T1


t_t1 = SchemaManager(schemas=[
      RowSchema(
            model=Tribal_TANF_T1,
            preparsing_validators=[
                  validators.hasLength(123),
            ],
            postparsing_validators=[
                  validators.if_then_validator(
                        condition_field='CASH_AMOUNT', condition_function=validators.isLargerThan(0),
                        result_field='NBR_MONTHS', result_function=validators.isLargerThan(0),
                  ),
                  validators.if_then_validator(
                        condition_field='CC_AMOUNT', condition_function=validators.isLargerThan(0),
                        result_field='CHILDREN_COVERED', result_function=validators.isLargerThan(0),
                  ),
                  validators.if_then_validator(
                        condition_field='CC_AMOUNT', condition_function=validators.isLargerThan(0),
                        result_field='CC_NBR_MONTHS', result_function=validators.isLargerThan(0),
                  ),
                  validators.if_then_validator(
                        condition_field='TRANSP_AMOUNT', condition_function=validators.isLargerThan(0),
                        result_field='TRANSP_NBR_MONTHS', result_function=validators.isLargerThan(0),
                  ),
                  validators.if_then_validator(
                        condition_field='TRANSITION_SERVICES_AMOUNT', condition_function=validators.isLargerThan(0),
                        result_field='TRANSITION_NBR_MONTHS', result_function=validators.isLargerThan(0),
                  ),
                  validators.if_then_validator(
                        condition_field='OTHER_AMOUNT', condition_function=validators.isLargerThan(0),
                        result_field='OTHER_NBR_MONTHS', result_function=validators.isLargerThan(0),
                  ),
                  validators.if_then_validator(
                        condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                        result_field='WORK_REQ_SANCTION', result_function=validators.oneOf((1, 2)),
                  ),
                  validators.if_then_validator(
                        condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                        result_field='FAMILY_SANC_ADULT', result_function=validators.oneOf((1, 2)),
                  ),
                  validators.if_then_validator(
                        condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                        result_field='SANC_TEEN_PARENT', result_function=validators.oneOf((1, 2)),
                  ),
                  validators.if_then_validator(
                        condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                        result_field='NON_COOPERATION_CSE', result_function=validators.oneOf((1, 2)),
                  ),
                  validators.if_then_validator(
                        condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                        result_field='FAILURE_TO_COMPLY', result_function=validators.oneOf((1, 2)),
                  ),
                  validators.if_then_validator(
                        condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                        result_field='OTHER_SANCTION', result_function=validators.oneOf((1, 2)),
                  ),
                  validators.if_then_validator(
                        condition_field='OTHER_TOTAL_REDUCTIONS', condition_function=validators.isLargerThan(0),
                        result_field='FAMILY_CAP', result_function=validators.oneOf((1, 2)),
                  ),
                  validators.if_then_validator(
                        condition_field='OTHER_TOTAL_REDUCTIONS', condition_function=validators.isLargerThan(0),
                        result_field='REDUCTIONS_ON_RECEIPTS', result_function=validators.oneOf((1, 2)),
                  ),
                  validators.if_then_validator(
                        condition_field='OTHER_TOTAL_REDUCTIONS', condition_function=validators.isLargerThan(0),
                        result_field='OTHER_NON_SANCTION', result_function=validators.oneOf((1, 2)),
                  ),
                  validators.sumIsLarger(("AMT_FOOD_STAMP_ASSISTANCE", "AMT_SUB_CC", "CASH_AMOUNT", "CC_AMOUNT",
                                          "TRANSP_AMOUNT", "TRANSITION_SERVICES_AMOUNT", "OTHER_AMOUNT"), 0)
            ],
            fields=[
                  Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
                        required=True, validators=[]),
                  Field(item="4", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
                        required=True, validators=[
                              validators.dateYearIsLargerThan(1998),
                              validators.dateMonthIsValid(),
                        ]),
                  Field(item="6", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
                        required=True, validators=[validators.isAlphaNumeric()]),
                  Field(item="2", name='COUNTY_FIPS_CODE', type='string', startIndex=19, endIndex=22,
                        required=False, validators=[
                              validators.isNumber(),
                        ]),
                  Field(item="5", name='STRATUM', type='string', startIndex=22, endIndex=24,
                        required=False, validators=[
                              validators.isInStringRange(0, 99),
                        ]),
                  Field(item="7", name='ZIP_CODE', type='string', startIndex=24, endIndex=29,
                        required=True, validators=[
                              validators.isNumber(),
                        ]),
                  Field(item="8", name='FUNDING_STREAM', type='number', startIndex=29, endIndex=30,
                        required=True, validators=[
                              validators.isInLimits(1, 2),
                        ]),
                  Field(item="9", name='DISPOSITION', type='number', startIndex=30, endIndex=31,
                        required=True, validators=[
                              validators.oneOf([1]),
                        ]),
                  Field(item="10", name='NEW_APPLICANT', type='number', startIndex=31, endIndex=32,
                        required=True, validators=[
                              validators.oneOf([1, 2]),
                        ]),
                  Field(item="11", name='NBR_FAMILY_MEMBERS', type='number', startIndex=32, endIndex=34,
                        required=True, validators=[
                              validators.isInLimits(1, 99),
                        ]),
                  Field(item="12", name='FAMILY_TYPE', type='number', startIndex=34, endIndex=35,
                        required=True, validators=[
                              validators.isInLimits(1, 3),
                        ]),
                  Field(item="13", name='RECEIVES_SUB_HOUSING', type='number', startIndex=35, endIndex=36,
                        required=True, validators=[
                              validators.isInLimits(1, 3),
                        ]),
                  Field(item="14", name='RECEIVES_MED_ASSISTANCE', type='number', startIndex=36, endIndex=37,
                        required=True, validators=[
                              validators.isInLimits(1, 2),
                        ]),
                  Field(item="15", name='RECEIVES_FOOD_STAMPS', type='number', startIndex=37, endIndex=38,
                        required=False, validators=[
                              validators.isInLimits(0, 2),
                        ]),
                  Field(item="16", name='AMT_FOOD_STAMP_ASSISTANCE', type='number', startIndex=38, endIndex=42,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="17", name='RECEIVES_SUB_CC', type='number', startIndex=42, endIndex=43,
                        required=False, validators=[
                              validators.isInLimits(0, 3),
                        ]),
                  Field(item="18", name='AMT_SUB_CC', type='number', startIndex=43, endIndex=47,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="19", name='CHILD_SUPPORT_AMT', type='number', startIndex=47, endIndex=51,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="20", name='FAMILY_CASH_RESOURCES', type='number', startIndex=51, endIndex=55,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="21A", name='CASH_AMOUNT', type='number', startIndex=55, endIndex=59,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="21B", name='NBR_MONTHS', type='number', startIndex=59, endIndex=62,
                        required=True, validators=[
                              validators.isInLimits(0, 999),
                        ]),
                  Field(item="22A", name='CC_AMOUNT', type='number', startIndex=62, endIndex=66,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="22B", name='CHILDREN_COVERED', type='number', startIndex=66, endIndex=68,
                        required=True, validators=[
                              validators.isInLimits(0, 99),
                        ]),
                  Field(item="22C", name='CC_NBR_MONTHS', type='number', startIndex=68, endIndex=71,
                        required=True, validators=[
                              validators.isInLimits(0, 999),
                        ]),
                  Field(item="23A", name='TRANSP_AMOUNT', type='number', startIndex=71, endIndex=75,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="23B", name='TRANSP_NBR_MONTHS', type='number', startIndex=75, endIndex=78,
                        required=True, validators=[
                              validators.isInLimits(0, 999),
                        ]),
                  Field(item="24A", name='TRANSITION_SERVICES_AMOUNT', type='number', startIndex=78, endIndex=82,
                        required=False, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="24B", name='TRANSITION_NBR_MONTHS', type='number', startIndex=82, endIndex=85,
                        required=False, validators=[
                              validators.isInLimits(0, 999),
                        ]),
                  Field(item="25A", name='OTHER_AMOUNT', type='number', startIndex=85, endIndex=89,
                        required=False, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="25B", name='OTHER_NBR_MONTHS', type='number', startIndex=89, endIndex=92,
                        required=False, validators=[
                              validators.isInLimits(0, 999),
                        ]),
                  Field(item="26AI", name='SANC_REDUCTION_AMT', type='number', startIndex=92, endIndex=96,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="26AII", name='WORK_REQ_SANCTION', type='number', startIndex=96, endIndex=97,
                        required=True, validators=[
                              validators.oneOf([1, 2]),
                        ]),
                  Field(item="26AIII", name='FAMILY_SANC_ADULT', type='number', startIndex=97, endIndex=98,
                        required=False, validators=[
                              validators.oneOf([0, 1, 2]),
                        ]),
                  Field(item="26AIV", name='SANC_TEEN_PARENT', type='number', startIndex=98, endIndex=99,
                        required=True, validators=[
                              validators.oneOf([1, 2]),
                        ]),
                  Field(item="26AV", name='NON_COOPERATION_CSE', type='number', startIndex=99, endIndex=100,
                        required=True, validators=[
                              validators.oneOf([1, 2]),
                        ]),
                  Field(item="26AVI", name='FAILURE_TO_COMPLY', type='number', startIndex=100, endIndex=101,
                        required=True, validators=[
                              validators.oneOf([1, 2]),
                        ]),
                  Field(item="26AVII", name='OTHER_SANCTION', type='number', startIndex=101, endIndex=102,
                        required=True, validators=[
                              validators.oneOf([1, 2]),
                        ]),
                  Field(item="26B", name='RECOUPMENT_PRIOR_OVRPMT', type='number', startIndex=102, endIndex=106,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="26CI", name='OTHER_TOTAL_REDUCTIONS', type='number', startIndex=106, endIndex=110,
                        required=True, validators=[
                              validators.isInLimits(0, 9999),
                        ]),
                  Field(item="26CII", name='FAMILY_CAP', type='number', startIndex=110, endIndex=111,
                        required=True, validators=[
                              validators.oneOf([1, 2]),
                        ]),
                  Field(item="26CIII", name='REDUCTIONS_ON_RECEIPTS', type='number', startIndex=111, endIndex=112,
                        required=True, validators=[
                              validators.oneOf([1, 2]),
                        ]),
                  Field(item="26CIV", name='OTHER_NON_SANCTION', type='number', startIndex=112, endIndex=113,
                        required=True, validators=[
                              validators.oneOf([1, 2]),
                        ]),
                  Field(item="27", name='WAIVER_EVAL_CONTROL_GRPS', type='string', startIndex=113, endIndex=114,
                        required=False, validators=[validators.isInStringRange(0, 9)]),
                  Field(item="28", name='FAMILY_EXEMPT_TIME_LIMITS', type='number', startIndex=114, endIndex=116,
                        required=True, validators=[validators.isInLimits(0, 9)]),
                  Field(item="29", name='FAMILY_NEW_CHILD', type='number', startIndex=116, endIndex=117,
                        required=False, validators=[
                              validators.oneOf([0, 1, 2]),
                        ]),
                  Field(item="-1", name='BLANK', type='string', startIndex=117, endIndex=123, required=False,
                        validators=[]),
            ],
      )]
)
