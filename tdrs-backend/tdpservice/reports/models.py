"""Define report models."""
from django.db import models
from ..files.models import File
from ..users.models import User
from ..stts.models import STT
# Create your models here.


class Report(models.Model):
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

class ReportFile(File):
    """Represents a version of a report file."""
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='report',
        blank=False,
        null=False
    )