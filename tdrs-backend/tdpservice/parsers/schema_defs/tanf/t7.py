"""Schema for TANF T7 Row."""

from ...util import SchemaManager
from ...fields import Field, TransformField
from ...row_schema import RowSchema
from ...transforms import calendar_quarter_to_rpt_month_year
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T7

schemas = []

validator_start_index = 7
section_ind_start_index = 7
stratum_start_index = 8
families_start_index = 10
for i in range(1, 31):
    schemas.append(
      RowSchema(
          model=TANF_T7,
          quiet_preparser_errors=i > 1,
          preparsing_validators=[
              validators.notEmpty(0, 7),
              validators.notEmpty(validator_start_index, validator_start_index + 24),
          ],
          postparsing_validators=[],
          fields=[
              Field(item="0", name="RecordType", type='string', startIndex=0, endIndex=2,
                    required=True, validators=[]),
              Field(item="3", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
                    required=True, validators=[validators.dateYearIsLargerThan(1998),
                                               validators.quarterIsValid()]),
              TransformField(calendar_quarter_to_rpt_month_year(i % 3), item="3A", name='RPT_MONTH_YEAR', type='number',
                             startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                                validators.dateMonthIsValid()]),
              Field(item="4", name='TDRS_SECTION_IND', type='string', startIndex=section_ind_start_index,
                    endIndex=section_ind_start_index + 1, required=True, validators=[validators.oneOf(['1', '2'])]),
              Field(item="5", name='STRATUM', type='string', startIndex=stratum_start_index,
                    endIndex=stratum_start_index + 2, required=True, validators=[validators.isInStringRange(1, 99)]),
              Field(item="6A", name='FAMILIES_MONTH', type='number', startIndex=families_start_index,
                    endIndex=families_start_index + 7, required=True, validators=[validators.isInLimits(0, 9999999)]),
          ]
      )
    )

    index_offset = 0 if i % 3 != 0 else 24
    validator_start_index += index_offset
    section_ind_start_index += index_offset
    stratum_start_index += index_offset
    families_start_index += 7 if i % 3 != 0 else 10

t7 = SchemaManager(schemas=schemas)
