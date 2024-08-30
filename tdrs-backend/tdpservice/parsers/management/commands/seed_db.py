"""`seed_db` command."""


import random
import logging

from django.core.management import BaseCommand
from faker import Faker
fake = Faker()
from django.core.files.base import ContentFile
from tdpservice.parsers.schema_defs.header import header
from tdpservice.parsers.schema_defs.trailer import trailer
from tdpservice.parsers.schema_defs.utils import *  # maybe need other utilities
from tdpservice.parsers.util import fiscal_to_calendar
# all models should be referenced by using the utils.py get_schema_options wrappers

from tdpservice.data_files.models import DataFile
from tdpservice.parsers import parse
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.scheduling.parser_task import parse as parse_task
from tdpservice.stts.models import STT
from tdpservice.users.models import User
from tdpservice.parsers.row_schema import RowSchema

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


def validValues(schemaMgr, field, year):
    '''Takes in a field and returns a line of valid values.'''

    field_len = field.endIndex - field.startIndex
    # check list of validators
        # treat header/trailer special, it actually checks for string values
        # check for zero or pad fill
        # transformField might be tricky
    if field.name == 'RecordType':
        return schemaMgr.record_type
    if field.name == 'SSN':
        # only used by recordtypes 2,3,5 
        # TODO: reverse the TransformField logic to 'encrypt' a random number
        field_format = '?' * field_len
    elif field.name in ('RPT_MONTH_YEAR', 'CALENDAR_QUARTER'):
        lower = 1 # TODO: get quarter and use acceptable range for month
        upper = 12
        # need to generate a two-digit month with leading zero using format() and randit()
        month = '{}'.format(random.randint(lower, upper)).zfill(2)
        field_format = '{}{}'.format(year, str(month))  # fake.date_time_this_month(before_now=True, after_now=False).strftime('%m%Y')
    else:
        field_format = '#' * field_len
    return fake.bothify(text=field_format)


def make_line(schemaMgr, section, year):
    '''Takes in a schema manager and returns a line of data.'''
    line = ''

    #row_schema = schemaMgr.schemas[0]
    for row_schema in schemaMgr.schemas:  # this is to handle multi-schema like T6
        for field in row_schema.fields:
            line += validValues(row_schema, field, year)
    return line + '\n'

def make_HT(schemaMgr, prog_type, section, year, quarter, stt):
    line = ''

    '''
    The following fields are defined in the schema for the HEADER row of all submission types:  
    1. title
    2. year
    3. quarter
    4. type
    5. state_fips
    6. tribe_code
    7. program_type
    8. edit
    9. encryption
    10. update
    '''
    if type(schemaMgr) is RowSchema:
        if schemaMgr.record_type == 'HEADER':
            # HEADER2020Q1CAL000TAN1ED
            for field in schemaMgr.fields:
                if field.name == 'title':
                    line += 'HEADER'
                elif field.name == 'year':
                    line += '{}'.format(year)
                elif field.name == 'quarter':
                    line += quarter[1:]  # remove the 'Q', e.g., 'Q1' -> '1'
                elif field.name == 'type':
                    line += section
                elif field.name == 'state_fips':
                    if stt.state is not None:  # this is a tribe
                        my_stt = stt.state
                    else:
                        my_stt = stt
                    line += '{}'.format(my_stt.stt_code).zfill(2)
                elif field.name == 'tribe_code':
                    if stt.type == 'tribe':
                        line += stt.stt_code
                    else:
                        line += '000'
                elif field.name == 'program_type':
                    line += prog_type
                elif field.name == 'edit':
                    line += '1'
                elif field.name == 'encryption':
                    line += 'E'
                elif field.name == 'update':
                    line += 'D'
                

            #line += 'HEADER{}1{}01   TAN1 D'.format(year, section)  # do I need to do that off-by-one thing on quarter
        elif schemaMgr.record_type == 'TRAILER':
            line += 'TRAILER' + '1' * 16
    else:
        print('Invalid record type')
        return None

    return line + '\n'

def make_files(stt, sub_year, sub_quarter):
    '''Given a STT, parameterize calls to build_datafile and make_line.'''
    sections = stt.filenames.keys()
    """ {'Active Case Data': 'ADS.E2J.FTP1.TS05', 'Closed Case Data': 'ADS.E2J.FTP2.TS05', 'Aggregate Data': 'ADS.E2J.FTP3.TS05'}"
    # "{'Active Case Data': 'ADS.E2J.NDM1.TS24', 'Closed Case Data': 'ADS.E2J.NDM2.TS24', 'Aggregate Data': 'ADS.E2J.NDM3.TS24', 
    #       'Stratum Data': 'ADS.E2J.NDM4.TS24', 'SSP Active Case Data': 'ADS.E2J.NDM1.MS24', 'SSP Closed Case Data': 'ADS.E2J.NDM2.MS24', 'SSP Aggregate Data': 
    #       'ADS.E2J.NDM3.MS24', 'SSP Stratum Data': 'ADS.E2J.NDM4.MS24'}"
    """
    files_for_quarter = {}


    for long_section in sections:
        # based on section, get models from schema_options
        #if stt.ssp is True:
        # we can match section to the schema_options
        # elif stt.state is not None:
        # we can declare prog_type to Tribal

        # given a leaf of 'section', get 'TAN' or 'SSP' or 'Tribal TAN' from schema_options
        
        # match schema_options[_]['section'] to our section
        text_dict = get_schema_options("", section=long_section, query='text')
        prog_type = text_dict['program_type'] # TAN
        section = text_dict['section']  # A
        models_in_section = get_program_models(prog_type, section)
        temp_file = ''

        '''
        def fiscal_to_calendar(year, fiscal_quarter):
            """Decrement the input quarter text by one."""
            array = [1, 2, 3, 4]  # wrapping around an array
            int_qtr = int(fiscal_quarter[1:])  # remove the 'Q', e.g., 'Q1' -> '1'
            if int_qtr == 1:
                year = year - 1

            ind_qtr = array.index(int_qtr)  # get the index so we can easily wrap-around end of array
            return year, "Q{}".format(array[ind_qtr - 1])  # return the previous quarter


        def calendar_to_fiscal(calendar_year, fiscal_quarter):
            """Decrement the calendar year if in Q1."""
            return calendar_year - 1 if fiscal_quarter == 'Q1' else calendar_year


        def transform_to_months(quarter):
            """Return a list of months in a quarter depending the quarter's format."""
            match quarter:
                case "Q1":
                    return ["Jan", "Feb", "Mar"]
        ....

        def month_to_int(month):
            """Return the integer value of a month."""
            return datetime.strptime(month, '%b').strftime('%m')
                calendar_year, calendar_quarter = get_calendar_quarter(year, quarter)
        '''



        cal_year, cal_quarter = fiscal_to_calendar(sub_year, 'Q{}'.format(sub_quarter))


        
        temp_file += make_HT(header, prog_type, section, cal_year, cal_quarter, stt)

        # iterate over models and generate lines
        for _, model in models_in_section.items():
            if long_section in ['Active Case Data', 'Closed Case Data','Aggregate Data', 'Stratum Data']:
                for i in range(random.randint(5, 9)):
                    temp_file += make_line(model,section, cal_year)
            #elif section in ['Aggregate Data', 'Stratum Data']:
            #    # we should generate a smaller count of lines...maybe leave this as a TODO
            #    # shouldn't this be based on the active/closed case data?
            #    pass

        # make trailer line
        temp_file += make_HT(trailer, prog_type, section, cal_year, cal_quarter, stt)
        #print(temp_file)
        
        datafile = build_datafile(
            stt=stt,
            year=sub_year,  # fiscal submission year
            quarter=f"Q{sub_quarter}",  # fiscal submission quarter
            original_filename=f'{stt}-{section}-{sub_year}Q{sub_quarter}.txt',
            file_name=f'{stt}-{section}-{sub_year}Q{sub_quarter}',
            section=long_section,
            file_data=bytes(temp_file.rstrip(), 'utf-8'),
        )
        datafile.save()
        files_for_quarter[section] = datafile

    return files_for_quarter

def make_seed():
    """Invokes scheduling/management/commands/backup_db management command."""
    from tdpservice.scheduling.management.commands.backup_db import Command as BackupCommand
    backup = BackupCommand()
    backup.handle(file = '/tdpapp/tdrs_db_seed.pg') # /tmp/tdrs_db_backup.pg')



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

        for stt in STT.objects.filter(id__in=range(1,2)):
        #get(id=1):  # all():
            for yr in range(2020, 2025):
                for qtr in [1,2,3,4]:
                    files_for_qtr = make_files(stt, yr, qtr)
                    print(files_for_qtr)
                    for f in files_for_qtr.keys():
                        df = files_for_qtr[f]
                        print(df.id)
                        #dfs = DataFileSummary.objects.create(datafile=df, status=DataFileSummary.Status.PENDING) #maybe i need df.file_data?
                        dfs = DataFileSummaryFactory.build()
                        dfs.datafile = df
                        #parse.parse_datafile(df, dfs)
                        parse_task(df.id, False)  # does this work too?

        # dump db in full using `make_seed` func
        make_seed()



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
        
