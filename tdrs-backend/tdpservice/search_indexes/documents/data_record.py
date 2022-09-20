from django_elasticsearch_dsl import Document, fields
from search_indexes.models import ParsedDataRecord

class DataRecordDocument(Document):
    class Django(object):
        model = ParsedDataRecord

    record = fields.StringField(analyzer=None, fields={'raw': fields.StringField(analyzer='keyword')})
    rpt_month_year = fields.IntegerField() # convert to date time?
    case_number = fields.StringField(analyzer=None, fields={'raw': fields.StringField(analyzer='keyword')})
    disposition = fields.IntegerField()
    fips_code = fields.StringField(analyzer=None, fields={'raw': fields.StringField(analyzer='keyword')})

    record_length = fields.IntegerFields(attr='record_length') # references computed property `record_length`