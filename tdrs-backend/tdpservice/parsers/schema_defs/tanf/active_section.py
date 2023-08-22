'''Contains the schema definition for the active section of the TANF program type.'''


#from . import t1, t2, t3 header, trailer
from tdpservice.parsers import util

'''TODO:
QTR - cat5/6 -- post parity
    activeSection  - cat4
        header - cat1,2
        t1 - cat2,3
        t2 
        t3
        trailer
    closedSection
        header
        t4
        t5 
        trailer
    stratum 
        num_applicants == active where joindate => qtr
'''

class SectionSchemaManager(util.SchemaManager):
    '''Schema manager for the active section of the TANF program type.'''

    def __init__(self, schema_managers, cases=[], validators=[]):
        '''Initializes the ActiveSectionSchemaManager with the schema managers for the active section.'''
        super().__init__(
            schemas=[schema.schemas for schema in schema_managers]
            # TODO: do i want to add header here? save the header record
        )
        self.cases = cases
        self.validators = validators

    def gather_cases(self, records):
        pass

    def set_validators(self, validators):
        self.validators = validators

    def get_header_rmy(self, header_record):
        # year = None
        # quarter = None
        # header = header_record
        # for field in header.fields:
        #     if field.name == 'year':
        #         year = field.value
        #     if field.name == 'quarter':
        #         quarter = field.value
        return f"{header_record['year']}{header_record['quarter']}"
    '''    
    def get_header_schema(self):
        for schema in self.schemas:
            for field in schema.fields:
                if field.name == 'title' and field.value == 'HEADER':
                    return schema
    '''
    def parse_and_validate(self, data_file, generate_error):
        '''Runs consistency checks for records of the datafile.'''

        header_rmy = self.get_header_rmy()
        month_list = util.transform_to_months(header_rmy)



        # TODO: date checks against header RMY
        # TODO: build out case structure
        # queryset for all records in scehmas matching case_number
        # for schema in schemas:
        #     records.append(schema.objects.filter(case_number=case_number))

        # CaseStruct(case_number, records)
        # CaseStruct.check_incosnsitensi
        # 
        print("we ran active section parse and validate")

# activeSection = SectionSchemaManager(
#     schema_managers=[  #TODO: use get_schema_options
#         t1.t1.schemas,
#         t2.t2.schemas,
#         t3.t3.schemas,
#         header.header.schemas,
#         trailer.trailer.schemas
#     ],
#     [validators]
# )



class CaseStruct():
    '''Represents an active case.'''
    def __init__(self, case_number):
        self.case_number = case_number
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def get_records(self):
        return self.records
    


        
