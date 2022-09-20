from django.conf import settings
from django_elasticsearch_dsl import Index, fields

from search_indexes.documents.data_record import DataRecordDocument
from search_indexes.models import T1
from search_indexes.analyzers import html_strip

# Name of the Elasticsearch index
ElasticSearchIndex = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
ElasticSearchIndex.settings(
    number_of_shards=1,
    number_of_replicas=1
)

@ElasticSearchIndex.doc_type
class T1DataSubmissionDocument(DataRecordDocument):
    class Django(object):
        model = T1

    county_fips_code = fields.StringField(analyzer=None, fields={'raw': fields.StringField(analyzer='keyword')})
    stratum = fields.IntegerField()
    zip_code = fields.StringField(analyzer=None, fields={'raw': fields.StringField(analyzer='keyword')})
    funding_stream = fields.IntegerField()
    new_applicant = fields.IntegerField()
    nbr_of_family_members = fields.IntegerField()
    family_type = fields.IntegerField()
    receives_sub_housing = fields.IntegerField()
    receives_medical_assistance = fields.IntegerField()
    receives_food_stamps = fields.IntegerField()
    amt_food_stamp_assistance = fields.IntegerField()
    receives_sub_cc = fields.IntegerField()
    amt_sub_cc = fields.IntegerField()
    cc_amount = fields.IntegerField()
    family_cash_recources = fields.IntegerField()
    cash_amount = fields.IntegerField()
    nbr_months = fields.IntegerField()
    cc_amount = fields.IntegerField()
    children_covered = fields.IntegerField()
    cc_nbr_of_months = fields.IntegerField()
    transp_amount = fields.IntegerField()
    transp_nbr_months = fields.IntegerField()
    transition_services_amount = fields.IntegerField()
    transition_nbr_months = fields.IntegerField()
    other_amount = fields.IntegerField()
    other_nbr_of_months = fields.IntegerField()
    sanc_reduction_amount = fields.IntegerField()
    work_req_sanction = fields.IntegerField()
    family_sanct_adult = fields.IntegerField()
    sanct_teen_parent = fields.IntegerField()
    non_cooperation_cse = fields.IntegerField()
    failure_to_comply = fields.IntegerField()
    other_sanction = fields.IntegerField()
    recoupment_prior_ovrpmt = fields.IntegerField()
    other_total_reductions = fields.IntegerField()
    family_cap = fields.IntegerField()
    reductions_on_receipts = fields.IntegerField()
    other_non_sanction = fields.IntegerField()
    waiver_evalu_control_grps = fields.IntegerField()
    family_exempt_time_limits = fields.IntegerField()
    family_new_child = fields.IntegerField()
    blank = fields.StringField(analyzer=None, fields={'raw': fields.StringField(analyzer='keyword')})
