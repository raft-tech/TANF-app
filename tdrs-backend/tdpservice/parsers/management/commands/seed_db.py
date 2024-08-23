"""`seed_db` command."""

import sys
import random
import logging
from pathlib import Path

from django.core.management import BaseCommand
from faker import Faker
fake = Faker()
from django.core.files.base import ContentFile
from tdpservice.parsers.test.factories import ParsingFileFactory, TanfT1Factory # maybe need other factories
from tdpservice.parsers.schema_defs.header import header
from tdpservice.parsers.schema_defs.trailer import trailer
from tdpservice.parsers.schema_defs.utils import *  # maybe need other utilities
# all models should be referenced by using the utils.py get_schema_options wrappers
from tdpservice.parsers import schema_defs
from tdpservice.data_files.models import DataFile
from tdpservice.scheduling import parser_task
from tdpservice.stts.models import STT
#import the system_user
from tdpservice.users.models import User


logger = logging.getLogger(__name__)

'''
Create a tool/mechanism for generating "random" and internally consistent data
    implement faker for test factories
    create datafile generator from factories

        class ParsingFileFactory(factory.django.DjangoModelFactory):
        # class DataFileSummaryFactory(factory.django.DjangoModelFactory):
        # class ParserErrorFactory(factory.django.DjangoModelFactory):
        class TanfT1Factory(factory.django.DjangoModelFactory):
        ...

    parse generated datafiles

Ensure tool is version/schema aware (we should be able to use django's migration table)
Tool will "fuzz" or generate out of range values to intentionally create issues [ stretch ]
    utilize parsers/schema_defs/utils.py as a reference for generating the `file__data` line by line
        have to start with header

        given a ParsingFileFactory, generate a file__data line by line

Create django command such that tool can be pointed at deployed environments 
'''



# t1 fields
'''
RecordType(0-2)
RPT_MONTH_YEAR(2-8)
CASE_NUMBER(8-19)
COUNTY_FIPS_CODE(19-22)
STRATUM(22-24)
ZIP_CODE(24-29)
FUNDING_STREAM(29-30)
DISPOSITION(30-31)
NEW_APPLICANT(31-32)
NBR_FAMILY_MEMBERS(32-34)
FAMILY_TYPE(34-35)
RECEIVES_SUB_HOUSING(35-36)
RECEIVES_MED_ASSISTANCE(36-37)
RECEIVES_FOOD_STAMPS(37-38)
AMT_FOOD_STAMP_ASSISTANCE(38-42)
RECEIVES_SUB_CC(42-43)
AMT_SUB_CC(43-47)
CHILD_SUPPORT_AMT(47-51)
FAMILY_CASH_RESOURCES(51-55)
CASH_AMOUNT(55-59)
NBR_MONTHS(59-62)
CC_AMOUNT(62-66)
CHILDREN_COVERED(66-68)
CC_NBR_MONTHS(68-71)
TRANSP_AMOUNT(71-75)
TRANSP_NBR_MONTHS(75-78)
TRANSITION_SERVICES_AMOUNT(78-82)
TRANSITION_NBR_MONTHS(82-85)
OTHER_AMOUNT(85-89)
OTHER_NBR_MONTHS(89-92)
SANC_REDUCTION_AMT(92-96)
WORK_REQ_SANCTION(96-97)
FAMILY_SANC_ADULT(97-98)
SANC_TEEN_PARENT(98-99)
NON_COOPERATION_CSE(99-100)
FAILURE_TO_COMPLY(100-101)
OTHER_SANCTION(101-102)
RECOUPMENT_PRIOR_OVRPMT(102-106)
OTHER_TOTAL_REDUCTIONS(106-110)
FAMILY_CAP(110-111)
REDUCTIONS_ON_RECEIPTS(111-112)
OTHER_NON_SANCTION(112-113)
WAIVER_EVAL_CONTROL_GRPS(113-114)
FAMILY_EXEMPT_TIME_LIMITS(114-116)
FAMILY_NEW_CHILD(116-117)
BLANK(117-156)
'''
# https://faker.readthedocs.io/en/stable/providers/baseprovider.html#faker.providers.BaseProvider
""" class FieldFaker(faker.providers.BaseProvider):
    def record_type(self):
        return self.random_element(elements=('00', '01', '02'))

    def rpt_month_year(self):
        return self.date_time_this_month(before_now=True, after_now=False).strftime('%m%Y')

    def case_number(self):
        return self.random_int(min=1000000000, max=9999999999)

    def county_fips_code(self):
        return self.random_int(min=0, max=999)

    def stratum(self):
        return self.random_int(min=0, max=99)

    def zip_code(self):
        return self.random_int(min=0, max=99999)

    def funding_stream(self):
        return self.random_element(elements=('A', 'B', 'C'))

    def disposition(self):
        return self.random_element(elements=('A', 'B', 'C'))

    def new_applicant(self):
        return self.random_element(elements=('Y', 'N'))

    def nbr_family_members(self):
        return self.random_int(min=0, max=99)

    def family_type(self):
        return self.random_element(elements=('A', 'B', 'C'))

    def receives_sub_housing(self):
        return self.random_element(elements=('Y', 'N'))
 """


def build_datafile(stt, year, quarter, original_filename, file_name, section, file_data):
    """Build a datafile."""
    
    try:
        d = DataFile.objects.create(
            user=User.objects.get_or_create(username='system')[0],
            stt=stt,
            year=year,
            quarter=quarter,
            original_filename=original_filename,
            section=section,
            version=random.randint(1, 1993415),
        )


        d.file.save(file_name, ContentFile(file_data))
    except django.db.utils.IntegrityError as e:
        pass
    return d


def validValues(schemaMgr, field):
    '''Takes in a field and returns a line of valid values.'''
    #niave implementation will just zero or 'a' fill the field
    '''field_len = field.endIndex - field.startIndex
    if field.type is "number":
        line += "0" * field_len
    elif field.type is "string":
        line += "A" * field_len
    else:
        raise ValueError("Field type not recognized")
    return line'''
    #brute implementation will use faker and we'll run it through the validators
    #pass

    # elegant implementation will use the validators to generate the valid values

    field_len = field.endIndex - field.startIndex
    # check list of validators
        # treat header/trailer special, it actually checks for string values
        # check for zero or pad fill
        # transformField might be tricky
    if field.name == 'RecordType':
        print(schemaMgr.record_type)
        return schemaMgr.record_type
    if field.name == 'SSN':
        # only used by recordtypes 2,3,5 
        # TODO: reverse the TransformField logic to 'encrypt' a random number
        field_format = '?' * field_len
    else:
        field_format = '#' * field_len
    return fake.bothify(text=field_format)

from tdpservice.parsers.row_schema import RowSchema
def make_line(schemaMgr, section):
    '''Takes in a schema manager and returns a line of data.'''
    line = ''

    #TODO: check for header/trailer
    if type(schemaMgr) is RowSchema:
            if schemaMgr.record_type == 'HEADER':
                line += 'HEADER20204{}01   TAN1 D'.format(section)
            elif schemaMgr.record_type == 'TRAILER':
                line += ' ' * 23
    else:
        row_schema = schemaMgr.schemas[0]
        for field in row_schema.fields:
            print(field)
            line += validValues(row_schema, field)

    print(line)
    return line + '\n'

from tdpservice.data_files.models import DataFile

def make_files(stt, year, quarter):
    '''Given a STT, parameterize calls to build_datafile and make_line.'''
    sections = stt.filenames.keys()
    # {'Active Case Data': 'ADS.E2J.FTP1.TS05', 'Closed Case Data': 'ADS.E2J.FTP2.TS05', 'Aggregate Data': 'ADS.E2J.FTP3.TS05'}"
    # "{'Active Case Data': 'ADS.E2J.NDM1.TS24', 'Closed Case Data': 'ADS.E2J.NDM2.TS24', 'Aggregate Data': 'ADS.E2J.NDM3.TS24', 
    #       'Stratum Data': 'ADS.E2J.NDM4.TS24', 'SSP Active Case Data': 'ADS.E2J.NDM1.MS24', 'SSP Closed Case Data': 'ADS.E2J.NDM2.MS24', 'SSP Aggregate Data': 
    #       'ADS.E2J.NDM3.MS24', 'SSP Stratum Data': 'ADS.E2J.NDM4.MS24'}"
    files_for_quarter = {}


    for s in sections:
        # based on section, get models from schema_options
        #if stt.ssp is True:
        # we can match section to the schema_options
        # elif stt.state is not None:
        # we can declare prog_type to Tribal

        # given a leaf of 'section', get 'TAN' or 'SSP' or 'Tribal TAN' from schema_options
        
        # match schema_options[_]['section'] to our section
        text_dict = get_schema_options("", section=s, query='text')
        prog_type = text_dict['program_type'] # TAN
        section = text_dict['section']  # A
        models_in_section = get_program_models(prog_type, section)
        temp_file = ''
        #TODO: make header line
        print("making file for section: ", section)
        temp_file += make_line(header,section)

        # iterate over models and generate lines
        for _, model in models_in_section.items():
            print(section)
            if s in ['Active Case Data', 'Closed Case Data','Aggregate Data', 'Stratum Data']:
                print('yes, secction in all of them')
                # obviously, this first approach can't prevent duplicates (unlikely),
                #    nor can it ensure that the case data is internally consistent
                #    (e.g. a case with a child but no adult)

                # we should generate hundreds, thousands, tens of thousands of records
                length = range(random.randint(5, 9))
                print(length)
                for i in length:
                    temp_file += make_line(model,section)
            #elif section in ['Aggregate Data', 'Stratum Data']:
            #    # we should generate a smaller count of lines...maybe leave this as a TODO
            #    # shouldn't this be based on the active/closed case data?
            #    pass

        # make trailer line
        temp_file += make_line(trailer,section)

        # build datafile
        # TODO convert temp_file to bytes literal
        datafile = build_datafile(
            stt=stt,
            year=year,
            quarter=quarter,
            original_filename=f'{section}.txt', #this is awful
            file_name=f'{section}.txt', #also bad
            section=section,
            file_data=bytes(temp_file, 'utf-8'),
        )
        datafile.save()
        files_for_quarter[section] = datafile

    return files_for_quarter

class Command(BaseCommand):
    """Command class."""

    help = "Populate datafiles, records, summaries, and errors for all STTs."

    def handle(self, *args, **options):
        """Populate datafiles, records, summaries, and errors for all STTs."""
   

        # from file__prog_type -> get me the prog type for referencing the schema_def
        """ def get_program_models(str_prog, str_section):
            def get_program_model(str_prog, str_section, str_model):
            def get_section_reference(str_prog, str_section):
            def get_text_from_df(df):
            def get_schema(line, section, program_type): """
    
    
        """ parsing_file = ParsingFileFactory.build(year=2021,
            quarter='Q2',
            original_filename='t3_file.txt',
            file__name='t3_file.txt',
            section=DataFile.Section.CLOSED_CASE_DATA,
            #**how do we make this**
            file__data=b'',  
        ) """
        #parsing_file.save()

        #x = get_text_from_df(parsing_file)
        #print(x)
    
        # t1 = schema_options.get('TAN').get('A').get('models').get('T1')
        #T1_fields = t1.schemas[0].fields

        #[print(i) for i in T1_fields]

        """ t1_line = ''
        for field in T1_fields:
            field_len = field.endIndex - field.startIndex
            # check list of validators
                # treat header/trailer special, it actually checks for string values
                # check for zero or pad fill
                # transformField might be tricky
            if field.name == 'SSN':
                # only used by recordtypes 2,3,5 
                # TODO: reverse the TransformField logic to 'encrypt' a random number
                field_format = '?' * field_len
            else:
                field_format = '#' * field_len
            t1_line += faker.bothify(text=field_format)
        print(t1_line) """

        # TODO: allowed values per field, try manual and if commonalities exist, create a function to generate
        # TODO: can we utilize validators somehow to get a validValues(schemaMgr.fields[])?
        from tdpservice.parsers.models import DataFileSummary
        from tdpservice.parsers import parse
        from tdpservice.parsers.test.factories import DataFileSummaryFactory
        files_for_qtr = make_files(STT.objects.get(id=1), 2024, 1)
        print(files_for_qtr)  # file has no id, and no payload/content
        for f in files_for_qtr.keys():
            df = files_for_qtr[f]
            #dfs = DataFileSummary.objects.create(datafile=df, status=DataFileSummary.Status.PENDING) #maybe i need df.file_data?
            dfs = DataFileSummaryFactory.build()
            dfs.datafile = df
            parse.parse_datafile(df, dfs)

        #files_for_qtr[0].save()

        # HALT
        # stts = STT.objects.all()
        # for stt in stts:
        #     print(stt)
        #     # for y in years[2024]
        #     for q in [1,2,3,4]:
        #         files_for_qtr = make_files(stt, 2024, q)
        #         print(files_for_qtr)
                # save to db or upload endpoint
                
                #for f in files_for_qtr:

                #    parser_task.parse(f.id, should_send_submission_email=False)
                # parse the file? or use DFS factory?
        # dump db in full


        '''TODO: try out parameterization like so:
        T2Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=1,
            ),
        '''

        '''
        # utilize parsers/schema_defs/utils.py as a reference for getting the lists of STT/years/quarters/sections
        for i in STT[]:
            for y in years[] # 2020-2022
                for q in quarters[] # 1-4
                    for p in programs[] # TAN, SSP, Tribal TAN
                        for s in sections[] # [x for x['section'] in schema_options[p].keys()]
                            #need the DF FK reference?
                            for m in models[]
                                for f in rowSchemas.Fields[]
                                    for v in f.validValues[]
                                    (look at seed_records.py for how to generate random data)
                            # write a temp file
                            # ok now parse this thing (but turn off emails)
                            # generate a DFS
        # dump db in full to a seed file
        '''
        
