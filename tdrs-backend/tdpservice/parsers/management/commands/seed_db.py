"""`seed_db` command."""

import json
import logging
from pathlib import Path

from django.core.management import BaseCommand
from django.utils import timezone

from tdpservice.parsers.schema_defs.utils import get_schema_options, get_text_from_df # maybe need other utilities
from tdpservice.parsers.test.factories import ParsingFileFactory, TanfT1Factory # maybe need other factories
from tdpservice.parsers.schema_defs.header import header
from tdpservice.parsers.schema_defs.tanf import t1, t2, t3, t4, t5, t6, t7
from tdpservice.parsers import schema_defs
from tdpservice.data_files.models import DataFile
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

schema_options = {
    'TAN': {
        'A': {
            'section': DataFile.Section.ACTIVE_CASE_DATA,
            'models': {
                'T1': schema_defs.tanf.t1,
                'T2': schema_defs.tanf.t2,
                'T3': schema_defs.tanf.t3,
            }
        },
        'C': {
            'section': DataFile.Section.CLOSED_CASE_DATA,
            'models': {
                'T4': schema_defs.tanf.t4,
                'T5': schema_defs.tanf.t5,
            }
        },
        'G': {
            'section': DataFile.Section.AGGREGATE_DATA,
            'models': {
                'T6': schema_defs.tanf.t6,
            }
        },
        'S': {
            'section': DataFile.Section.STRATUM_DATA,
            'models': {
                'T7': schema_defs.tanf.t7,
            }
        }
    },
    'SSP': {
        'A': {
            'section': DataFile.Section.SSP_ACTIVE_CASE_DATA,
            'models': {
                'M1': schema_defs.ssp.m1,
                'M2': schema_defs.ssp.m2,
                'M3': schema_defs.ssp.m3,
            }
        },
        'C': {
            'section': DataFile.Section.SSP_CLOSED_CASE_DATA,
            'models': {
                'M4': schema_defs.ssp.m4,
                'M5': schema_defs.ssp.m5,
            }
        },
        'G': {
            'section': DataFile.Section.SSP_AGGREGATE_DATA,
            'models': {
                'M6': schema_defs.ssp.m6,
            }
        },
        'S': {
            'section': DataFile.Section.SSP_STRATUM_DATA,
            'models': {
                'M7': schema_defs.ssp.m7,
            }
        }
    },
    'Tribal TAN': {
        'A': {
            'section': DataFile.Section.TRIBAL_ACTIVE_CASE_DATA,
            'models': {
                'T1': schema_defs.tribal_tanf.t1,
                'T2': schema_defs.tribal_tanf.t2,
                'T3': schema_defs.tribal_tanf.t3,
            }
        },
        'C': {
            'section': DataFile.Section.TRIBAL_CLOSED_CASE_DATA,
            'models': {
                'T4': schema_defs.tribal_tanf.t4,
                'T5': schema_defs.tribal_tanf.t5,
            }
        },
        'G': {
            'section': DataFile.Section.TRIBAL_AGGREGATE_DATA,
            'models': {
                'T6': schema_defs.tribal_tanf.t6,
            }
        },
        'S': {
            'section': DataFile.Section.TRIBAL_STRATUM_DATA,
            'models': {
                'T7': schema_defs.tribal_tanf.t7,
            }
        },
    },
}

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

        x = get_text_from_df(parsing_file)
        print(x)
    
        # t1 = schema_options.get('TAN').get('A').get('models').get('T1')
        T1_fields = t1.schemas[0].fields
        [print(i) for i in T1_fields]

        t1_line = ''
        for field in T1_fields:
            field_len = field.endIndex - field.startIndex
            if field.type is "number":
                t1_line += "0" * field_len
            elif field.type is "string":
                t1_line += "a" * field_len
            else:
                raise ValueError("Field type not recognized")
        print(t1_line)

        # TODO: allowed values per field, try manual and if commonalities exist, create a function to generate
        # TODO: can we utilize validators somehow to get a validValues(schemaMgr.fields[])?
  
        def validValues():
            '''Takes in a field and returns a list of valid values.'''
            #niave implementation will just zero or 'a' fill the field
            #brute implementation will use faker and we'll run it through the validators
            # elegant implementation will use the validators to generate the valid values
            pass


        '''
        # utilize parsers/schema_defs/utils.py as a reference for getting the lists of STT/years/quarters/sections
        for i in STT[]:
            for y in years[]
                for q in quarters[]
                    for s in sections[]
                        # now we're generating a binary file? b/c we'll need the DF FK reference
                        # TODO: 
                        for r in rowSchemas[]
                            for f in rowSchemas.Fields[]
                                for v in f.validValues[]
                                (look at seed_records.py for how to generate random data)
                        # write a temp file
                        # ok now parse this thing (but turn off emails)
                        # generate a DFS
        # dump db in full to a seed file
        '''
        
