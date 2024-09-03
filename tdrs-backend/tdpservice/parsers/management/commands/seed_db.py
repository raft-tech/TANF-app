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
#from tdpservice.parsers import parse
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.scheduling.parser_task import parse as parse_task
from tdpservice.stts.models import STT
from tdpservice.users.models import User
from tdpservice.parsers.row_schema import RowSchema

logger = logging.getLogger(__name__)

# https://faker.readthedocs.io/en/stable/providers/baseprovider.html#faker.providers.BaseProvider
""" class FieldFaker(faker.providers.BaseProvider):..."""

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

    if field.name == 'RecordType':
        return schemaMgr.record_type
    if field.name == 'SSN':
        # only used by recordtypes 2,3,5 
        # TODO: reverse the TransformField logic to 'encrypt' a random number
        field_format = '?' * field_len
    elif field.name in ('RPT_MONTH_YEAR', 'CALENDAR_QUARTER'):
        lower = 1 # TODO: get quarter and use acceptable range for month
        upper = 12

        month = '{}'.format(random.randint(lower, upper)).zfill(2)
        field_format = '{}{}'.format(year, str(month))
    else:
        field_format = '#' * field_len
    return fake.bothify(text=field_format)


def make_line(schemaMgr, section, year):
    '''Takes in a schema manager and returns a line of data.'''
    line = ''

    for row_schema in schemaMgr.schemas:  # this is to handle multi-schema like T6
        for field in row_schema.fields:
            line += validValues(row_schema, field, year)
    return line + '\n'

def make_HT(schemaMgr, prog_type, section, year, quarter, stt):
    line = ''

    if type(schemaMgr) is RowSchema:
        if schemaMgr.record_type == 'HEADER':
            # e.g. HEADER20201CAL000TAN1ED
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
                
        elif schemaMgr.record_type == 'TRAILER':
            line += 'TRAILER' + '1' * 16
    else:
        print('Invalid record type')
        return None

    return line + '\n'

def make_files(stt, sub_year, sub_quarter):
    '''Given a STT, parameterize calls to build_datafile and make_line.'''
    sections = stt.filenames.keys()
    files_for_quarter = {}


    for long_section in sections:
        text_dict = get_schema_options("", section=long_section, query='text')
        prog_type = text_dict['program_type'] # TAN
        section = text_dict['section']  # A
        models_in_section = get_program_models(prog_type, section)
        temp_file = ''

        cal_year, cal_quarter = fiscal_to_calendar(sub_year, 'Q{}'.format(sub_quarter))


        
        temp_file += make_HT(header, prog_type, section, cal_year, cal_quarter, stt)

        # iterate over models and generate lines
        for _, model in models_in_section.items():
            if long_section in ['Active Case Data', 'Closed Case Data','Aggregate Data', 'Stratum Data']:
                for i in range(random.randint(5, 999)):
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
    backup.handle(file = '/tdpapp/tdrs_db_seed.pg')

class Command(BaseCommand):
    """Command class."""

    help = "Populate datafiles, records, summaries, and errors for all STTs."

    def handle(self, *args, **options):
        """Populate datafiles, records, summaries, and errors for all STTs."""
   
        for stt in STT.objects.all():  # filter(id__in=range(1,2)):
            for yr in range(2020, 2025):
                for qtr in [1,2,3,4]:
                    files_for_qtr = make_files(stt, yr, qtr)
                    print(files_for_qtr)
                    for f in files_for_qtr.keys():
                        df = files_for_qtr[f]
                        dfs = DataFileSummaryFactory.build()
                        dfs.datafile = df
                        #parse.parse_datafile(df, dfs)
                        parse_task(df.id, False)

        # dump db in full using `make_seed` func
        make_seed()
        
