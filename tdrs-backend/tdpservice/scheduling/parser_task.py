"""Celery hook for parsing tasks."""
from __future__ import absolute_import
from celery import shared_task
import logging
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.parse import parse_datafile
from tdpservice.parsers.models import DataFileSummary
from tdpservice.parsers.util import case_aggregates_by_month, get_text_from_df, get_program_models
# from tdpservice.stts.models import STT

logger = logging.getLogger(__name__)


@shared_task
def parse(data_file_id):
    """Send data file for processing."""
    # passing the data file FileField across redis was rendering non-serializable failures, doing the below lookup
    # to avoid those. I suppose good practice to not store/serializer large file contents in memory when stored in redis
    # for undetermined amount of time.
    data_file = DataFile.objects.get(id=data_file_id)

    logger.info(f"DataFile parsing started for file {data_file.filename}")

    dfs = DataFileSummary.objects.create(datafile=data_file, status=DataFileSummary.Status.PENDING)
    errors = parse_datafile(data_file)
    dfs.status = dfs.get_status()
    dfs.case_aggregates = case_aggregates_by_month(data_file, dfs.status)
    dfs.save()

    if dfs.status == DataFileSummary.Status.ACCEPTED:
        # kick off submission validation
        submission_validation.apply_async(args=[data_file_id])
        pass
    # do I want to put in another redis task with stt/qtr/year?
    # this would allow us to check that all files have finished processing with accepted status

    # kick off cat4 processing
    # instatiate some cat4 processing class
    # call some method on that class to kick off processing
    # pass in the data_file to that method
    # that method will then kick off the processing
    # that method will also kick off the processing of the next file in the queue

    logger.info(f"DataFile parsing finished with status {dfs.status} and {len(errors)} errors: {errors}")


class Cat4Thing():
    def __init__(self, data_file):
        self.data_file = data_file

    def validate(self):
        # we need to lookup relevant cat4 validators for this section

        str_prog, str_section = get_text_from_df(self.data_file)
        models = get_program_models(str_prog, str_section)

        for model in models.values():
            

        
        # we need to run those validators against the models tagged to this guy
        # we need to generate relevant parserErrors


@shared_task
def submission_validation(data_file_id):
    """Send data file for quarter-wide submission validation."""
    # this is just a stub for cat4 stuff but we might lay groundwork for cat5/6
    #instatiate some cat4 processing class
    data_file = DataFile.objects.get(id=data_file_id)
    cat4 = Cat4Thing(data_file)



'''
    # check that all files have finished processing with accepted status for a given stt/year/qtr
    # if so, kick off cat5 processing
    
    datafiles_by_qtr = DataFile.objects.filter(stt=datafile.stt, year=datafile.fiscal_year, qtr=datafile.quarter)
    expected_sections = STT.objects.get(id=datafile.stt.id).filenames.keys()  # should render a list of section strings

    # check that all expected sections are in the datafiles_by_qtr
    for section in expected_sections:
        # handle prepending of "Tribal" if stt is tribal
        if datafile.stt.type == 'tribe':
            section = 'Tribal' + section

        if datafiles_by_qtr.filter(section=section).count() == 0:
            # if not, do nothing, put a message in the queue to check again in 5 minutes
            submission_validation.apply_async(args=[data_file_id], countdown=300)  # I have no idea if this is valid.
            pass
    
    # if so, check that all datafiles_by_qtr have a status of accepted
    dfs = DataFileSummary.objects.filter(data_file__in=datafiles_by_qtr).filter(status=DataFileSummary.Status.ACCEPTED)
    
    # if not, do nothing, put a message in the queue to check again in 5 minutes
    pass




    meta_parent_class.process(data_file)

    # we subclass the meta_parent_class to create a new class for each section

    class meta_parent_class:
        def __init__(self, stt, year, qtr):
             # go fetch all datafiles as a list in given quarter for given stt
            self.data_files = DataFile.objects.filter(stt=stt, year=year, qtr=qtr)

        def process(data_file):
            # from datafile get stt.filenames
            # iterate over filenames to get relevant sections
            # instantiate a new class for each section
'''
