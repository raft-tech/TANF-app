"""Elasticsearch document mappings for TANF submission models."""

from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from ..models.tanf import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5, TANF_T6, TANF_T7


@registry.register_document
class TANF_T1DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T1 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t1_submissions'
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
    """Elastic search model mapping for a parsed TANF T2 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t2_submissions'
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
            'RACE_HISPANIC_OR_LATINO',
            'RACE_AMERICAN_INDIAN_OR_ALASKA_NATIVE',
            'RACE_ASIAN',
            'RACE_BLACK_OR_AFRICAN_AMERICAN',
            'RACE_NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER',
            'RACE_WHITE',
            'GENDER',
            'RECEIVES_FEDERAL_DISABILITY_INSURANCE_OASDI_PROGRAM',
            'RECEIVES_BENEFITS_BASED_ON_FEDERAL_DISABILITY_STATUS',
            'RECEIVES_AID_TOTALLY_DISABLED_UNDER_TITLE_XIV_APDT',
            'RECEIVES_AID_TO_THE_AGED',
            'RECEIVES_SUPPLEMENTAL_SECURITY_INCOME_TITLE_XVI_SSI',
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
            'WORK_EXP_HOURS_OF_PARTICIPATION',
            'WORK_EXP_EXCUSED_ABSENCES',
            'WORK_EXP_HOLIDAYS',
            'ON_THE_JOB_TRAINING',
            'JOB_SEARCH_HOURS_OF_PARTICIPATION',
            'JOB_SEARCH_EXCUSED_ABSENCES',
            'JOB_SEARCH_HOLIDAYS',
            'COMMUNITY_SVS_HOURS_OF_PARTICIPATION',
            'COMMUNITY_SVS_EXCUSED_ABSENCES',
            'COMMUNITY_SVS_HOLIDAYS',
            'VOCATIONAL_ED_HOURS_OF_PARTICIPATION',
            'VOCATIONAL_ED_EXCUSED_ABSENCES',
            'VOCATIONAL_ED_HOLIDAYS',
            'JOB_SKILLS_HOURS_OF_PARTICIPATION',
            'JOB_SKILLS_EXCUSED_ABSENCES',
            'JOB_SKILLS_HOLIDAYS',
            'EDUCATION_RELATED_HOURS_OF_PARTICIPATION',
            'EDUCATION_RELATED_EXCUSED_ABSENCES',
            'EDUCATION_RELATED_HOLIDAYS',
            'SCHOOL_ATTENDENCE_HOURS_OF_PARTICIPATION',
            'SCHOOL_ATTENDENCE_EXCUSED_ABSENCES',
            'SCHOOL_ATTENDENCE_HOLIDAYS',
            'CHILD_CARE_HOURS_OF_PARTICIPATION',
            'CHILD_CARE_EXCUSED_ABSENCES',
            'CHILD_CARE_HOLIDAYS',
            'OTHER_WORK_ACTIVITIES',
            'NUMBER_OF_DEEMED_CORE_HOURS_FOR_OVERALL_RATE',
            'NUMBER_OF_DEEMED_CORE_HOURS_FOR_TWO_PARENT_RATE',
            'AMOUNT_OF_EARNED_INCOME',
            'UNEARNED_INCOME_EARNED_INCOME_TAX_CREDIT',
            'UNEARNED_INCOME_SOCIAL_SECURITY',
            'UNEARNED_INCOME_SSI',
            'UNEARNED_INCOME_WORKERS_COMPENSATION',
            'UNEARNED_INCOME_OTHER_UNEARNED_INCOME',
        ]


@registry.register_document
class TANF_T3DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T3 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t3_submissions'
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
            'RACE_HISPANIC_OR_LATINO',
            'RACE_AMERICAN_INDIAN_OR_ALASKA_NATIVE',
            'RACE_ASIAN',
            'RACE_BLACK_OR_AFRICAN_AMERICAN',
            'RACE_NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER',
            'RACE_WHITE',
            'GENDER',
            'RECEIVES_BENEFITS_UNDER_NON_SSA_PROGRAMS',
            'RECEIVES_SSI_UNDER_TITLE_XVI_SSI',
            'RELATIONSHIP_TO_HEAD_OF_HOUSEHOLD',
            'PARENT_WITH_MINOR_CHILD',
            'EDUCATION_LEVEL',
            'CITIZENSHIP_ALIENAGE',
            'UNEARNED_INCOME_SSI',
            'UNEARNED_INCOME_OTHER_UNEARNED_INCOME',
        ]


@registry.register_document
class TANF_T4DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T4 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t4_submissions'
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
    """Elastic search model mapping for a parsed TANF T5 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t5_submissions'
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
    """Elastic search model mapping for a parsed TANF T6 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t6_submissions'
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
    """Elastic search model mapping for a parsed TANF T7 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t7_submissions'
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
