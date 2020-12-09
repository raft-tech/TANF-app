"""Define report models."""

from django.db import models
from ..files.models import File
from ..users.models import User
from ..stts.models import STT

class ReportFile(models.Model):
    """Represents a version of a report file."""
    name = models.CharField(
        max_length=256,
        blank = False,
        null= False
    )
    section = models.CharField(
        
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user",
        blank=False,
        null=False
    )
    stt = models.ForeignKey(
        STT,
        on_delete=models.CASCADE,
        related_name='stt',
        blank=False,
        null=False
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
