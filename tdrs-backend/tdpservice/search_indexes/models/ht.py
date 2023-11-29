"""Houses the header and trailer models."""

import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import ParserError



class Header(models.Model):
    """
    Parsed record representing a Header data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='t1_parent'
    )

    error = GenericRelation(ParserError)
    TITLE = models.CharField(max_length=6, null=False, blank=False)
    YEAR = models.IntegerField(null=True, blank=False)
    QUARTER = models.CharField(max_length=1, null=False, blank=False)
    TYPE = models.CharField(max_length=1, null=False, blank=False)
    STATE_FIPS = models.CharField(max_length=2, null=False, blank=False)
    TRIBE_CODE = models.CharField(max_length=3, null=True, blank=True)
    PROGRAM_TYPE = models.CharField(max_length=3, null=False, blank=False)
    EDIT = models.CharField(max_length=1, null=False, blank=False)
    ENCRYPTION = models.CharField(max_length=1, null=True, blank=True)
    UPDATE = models.CharField(max_length=1, null=False, blank=False)

# class Trailer(models.Model):
#     """Parsed record representing a Trailer data submission."""

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     datafile = models.ForeignKey(
#         DataFile,
#         blank=True,
#         help_text='The parent file from which this record was created.',
#         null=True,
#         on_delete=models.CASCADE,
#         related_name='t1_parent'
#     )

#     error = GenericRelation(ParserError)
