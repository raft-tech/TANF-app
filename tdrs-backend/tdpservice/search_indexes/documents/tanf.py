"""Elasticsearch document mappings for TANF submission models."""

from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from ..models.tanf import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5, TANF_T6, TANF_T7


@registry.register_document
class TANF_T1DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T1 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't1_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T1
        fields = [
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'COUNTY_FIPS_CODE',
            'STRATUM',
            'ZIP_CODE',
            'FUNDING_STREAM',
            'DISPOSITION',
            'NEW_APPLICANT',
            'NBR_FAMILY_MEMBERS',
            'FAMILY_TYPE',
            'RECEIVES_SUB_HOUSING',
            'RECEIVES_MED_ASSISTANCE',
            'RECEIVES_FOOD_STAMPS',
            'AMT_FOOD_STAMP_ASSISTANCE',
            'RECEIVES_SUB_CC',
            'AMT_SUB_CC',
            'CHILD_SUPPORT_AMT',
            'FAMILY_CASH_RESOURCES',
            'CASH_AMOUNT',
            'NBR_MONTHS',
            'CC_AMOUNT',
            'CHILDREN_COVERED',
            'CC_NBR_MONTHS',
            'TRANSP_AMOUNT',
            'TRANSP_NBR_MONTHS',
            'TRANSITION_SERVICES_AMOUNT',
            'TRANSITION_NBR_MONTHS',
            'OTHER_AMOUNT',
            'OTHER_NBR_MONTHS',
            'SANC_REDUCTION_AMT',
            'WORK_REQ_SANCTION',
            'FAMILY_SANC_ADULT',
            'SANC_TEEN_PARENT',
            'NON_COOPERATION_CSE',
            'FAILURE_TO_COMPLY',
            'OTHER_SANCTION',
            'RECOUPMENT_PRIOR_OVRPMT',
            'OTHER_TOTAL_REDUCTIONS',
            'FAMILY_CAP',
            'REDUCTIONS_ON_RECEIPTS',
            'OTHER_NON_SANCTION',
            'WAIVER_EVAL_CONTROL_GRPS',
            'FAMILY_EXEMPT_TIME_LIMITS',
            'FAMILY_NEW_CHILD'
        ]


@registry.register_document
class TANF_T2DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T2 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't2_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T2
        fields = [
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',

            'FAMILY_AFFILIATION',
            'NONCUSTODIAL_PARENT',
            'DOB',
            'SSN',
            'ITEM34A_HISPANIC_OR_LATINO',
            'ITEM34B_AMERICAN_INDIAN_OR_ALASKA_NATIVE',
            'ITEM34C_ASIAN',
            'ITEM34D_BLACK_OR_AFRICAN_AMERICAN',
            'ITEM34E_NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER',
            'ITEM34F_WHITE',
            'GENDER',
            'ITEM36A_RECEIVES_FEDERAL_DISABILITY_INSURANCE_OASDI_PROGRAM',
            'ITEM36B_RECEIVES_BENEFITS_BASED_ON_FEDERAL_DISABILITY_STATUS',
            'ITEM36C_RECEIVES_AID_TO_THE_PERMANENTLY_AND_TOTALLY_DISABLED_UNDER_TITLE_XIV',
            'ITEM36D_RECEIVES_AID_TO_THE_AGED',
            'ITEM36E_RECEIVES_SUPPLEMENTAL_SECURITY_INCOME_UNDER_TITLE_XVI',
            'MARITAL_STATUS',
            'RELATIONSHIP_TO_HEAD_OF_HOUSEHOLD',
            'PARENT_WITH_MINOR_CHILD',
            'NEEDS_OF_A_PREGNANT_WOMAN',
            'EDUCATION_LEVEL',
            'CITIZENSHIP_STATUS',
            'COOPERATION_WITH_CHILD_SUPPORT',
            'NUMBER_OF_COUNTABLE_MONTHS',
            'NUMBER_OF_COUNTABLE_MONTHS_REMAINING',
            'CURRENT_MONTH_EXEMPT_FROM_STATE',
            'EMPLOYMENT_STATUS',
            'WORK_ELIGIBLE_INDIVIDUAL_INDICATOR',
            'WORK_PARTICIPATION_STATUS',
            'UNSUBSIDIZED_EMPLOYMENT',
            'SUBSIDIZED_PRIVATE_EMPLOYMENT',
            'SUBSIDIZED_PUBLIC_EMPLOYMENT',
            'ITEM53A_HOURS_OF_PARTICIPATION',
            'ITEM53B_EXCUSED_ABSENCES',
            'ITEM53C_HOLIDAYS',
            'ON_THE_JOB_TRAINING',
            'ITEM55A_HOURS_OF_PARTICIPATION',
            'ITEM55B_EXCUSED_ABSENCES',
            'ITEM55C_HOLIDAYS',
            'ITEM56A_HOURS_OF_PARTICIPATION',
            'ITEM56B_EXCUSED_ABSENCES',
            'ITEM56C_HOLIDAYS',
            'ITEM57A_HOURS_OF_PARTICIPATION',
            'ITEM57B_EXCUSED_ABSENCES',
            'ITEM57C_HOLIDAYS',
            'ITEM58A_HOURS_OF_PARTICIPATION',
            'ITEM58B_EXCUSED_ABSENCES',
            'ITEM58C_HOLIDAYS',
            'ITEM59A_HOURS_OF_PARTICIPATION',
            'ITEM59B_EXCUSED_ABSENCES',
            'ITEM59C_HOLIDAYS',
            'ITEM60A_HOURS_OF_PARTICIPATION',
            'ITEM60B_EXCUSED_ABSENCES',
            'ITEM60C_HOLIDAYS',
            'ITEM61A_HOURS_OF_PARTICIPATION',
            'ITEM61B_EXCUSED_ABSENCES',
            'ITEM61C_HOLIDAYS',
            'OTHER_WORK_ACTIVITIES',
            'NUMBER_OF_DEEMED_CORE_HOURS_FOR_OVERALL_RATE',
            'NUMBER_OF_DEEMED_CORE_HOURS_FOR_TWO_PARENT_RATE',
            'AMOUNT_OF_EARNED_INCOME',
            'ITEM66A_EARNED_INCOME_TAX_CREDIT',
            'ITEM66B_SOCIAL_SECURITY',
            'ITEM66C_SSI',
            'ITEM66D_WORKERS_COMPENSATION',
            'ITEM66E_OTHER_UNEARNED_INCOME',
        ]


@registry.register_document
class TANF_T3DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T3 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't3_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T3
        fields = [
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'FAMILY_AFFILIATION',
            'DOB',
            'SSN',
            'ITEM70A_HISPANIC_OR_LATINO',
            'ITEM70B_AMERICAN_INDIAN_OR_ALASKA_NATIVE',
            'ITEM70C_ASIAN',
            'ITEM70D_BLACK_OR_AFRICAN_AMERICAN',
            'ITEM70E_NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER',
            'ITEM70F_WHITE',
            'GENDER',
            'ITEM72A_RECEIVES_BENEFITS_BASED_ON_FEDERAL_DISABILITY_STATUS_UNDER_NON',
            'ITEM72B_RECEIVES_SSI_UNDER_TITLE_XVI_SSI',
            'RELATIONSHIP_TO_HEAD_OF_HOUSEHOLD',
            'PARENT_WITH_MINOR_CHILD',
            'EDUCATION_LEVEL',
            'CITIZENSHIP_ALIENAGE',
            'ITEM77A_SSI',
            'ITEM77B_OTHER_UNEARNED_INCOME',
        ]


@registry.register_document
class TANF_T4DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T4 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't4_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T4
        fields = [
            'record',
            'rpt_month_year',
            'case_number',
            'disposition',
            'fips_code',

            'county_fips_code',
            'stratum',
            'zip_code',
            'closure_reason',
            'rec_sub_housing',
            'rec_med_assist',
            'rec_food_stamps',
            'rec_sub_cc',
        ]


@registry.register_document
class TANF_T5DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T5 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't5_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T5
        fields = [
            'record',
            'rpt_month_year',
            'case_number',
            'fips_code',

            'family_affiliation',
            'date_of_birth',
            'ssn',
            'race_hispanic',
            'race_amer_indian',
            'race_asian',
            'race_black',
            'race_hawaiian',
            'race_white',
            'gender',
            'rec_oasdi_insurance',
            'rec_federal_disability',
            'rec_aid_totally_disabled',
            'rec_aid_aged_blind',
            'rec_ssi',
            'marital_status',
            'relationship_hoh',
            'parent_minor_child',
            'needs_of_pregnant_woman',
            'education_level',
            'citizenship_status',
            'countable_month_fed_time',
            'countable_months_state_tribe',
            'employment_status',
            'amount_earned_income',
            'amount_unearned_income',
        ]


@registry.register_document
class TANF_T6DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T6 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't6_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T6
        fields = [
            'record',
            'rpt_month_year',
            'fips_code',

            'calendar_quarter',
            'applications',
            'approved',
            'denied',
            'assistance',
            'families',
            'num_2_parents',
            'num_1_parents',
            'num_no_parents',
            'recipients',
            'adult_recipients',
            'child_recipients',
            'noncustodials',
            'births',
            'outwedlock_births',
            'closed_cases',
        ]


@registry.register_document
class TANF_T7DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T7 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't7_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T7
        fields = [
            'record',
            'rpt_month_year',
            'fips_code',

            'calendar_quarter',
            'tdrs_section_ind',
            'stratum',
            'families',
        ]
