"""Define report models."""

from django.db import models

from ..stts.models import STT
from ..users.models import User


# The Report File model was starting to explode, and I think that keeping this logic
# in its own abstract class is better for documentation purposes.
class File(models.Model):
    """Abstract type representing a file stored in S3"""
    class Meta:
        abstract = True

    original_filename = models.CharField(
        max_length=256,
        blank = False,
        null= False
    )

    slug = models.CharField(
        unique=True,
        max_length=256,
        blank = False,
        null= False
    )
    extension = models.CharField(
        max_length=8,
        default="txt"
    )
class ReportFile(File):
    """Represents a version of a report file."""
    class Section(models.TextChoices):
        """Enum for report section."""
        ACTIVE_CASE_DATA = "Active Case Data"
        CLOSE_CASE_DATA = "Close Case Data"
        AGGREGATE_DATA = "Aggregate Data"
        STRATUM_DATA = "Stratum Data"
    class Quarter(models.TextChoices):
        """Enum for report Quarter"""
        Q1 = "Q1"
        Q2 = "Q2"
        Q3 = "Q3"
        Q4 = "Q4"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ("section","version","quarter","year"),
                name = 'constraint_name')]

    version = models.IntegerField()
    year = models.IntegerField()
    section = models.CharField(
        max_length=200, blank=True, null=True, choices=Section.choices)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user",
        blank=False,
        null=False)
    # I don't think we actually need an STT here, cause the user has an STT.
    # I will use a serializer method to extract it from
    # stt = models.ForeignKey(
    #     STT,
    #     on_delete=models.CASCADE,
    #     related_name='stt',
    #     blank=False,
    #     null=False
    # )
