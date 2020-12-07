"""Define file model."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from ..users.models import User
from ..stts.models import STT

class File(models.Model):
    """A model representing a file stored in AWS s3 via cloud.gov."""
    slug = models.CharField(
        unique=True,
        max_length=256,
        blank = False,
        null= False
    )
    type = models.CharField(
        max_length=8,
        default="txt"
    )
    name = models.CharField(
        max_length=256,
        blank = False,
        null= False
    )
