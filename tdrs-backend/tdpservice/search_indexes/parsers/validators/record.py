from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
"""Wrapper around Django's RegexValidator."""

def record(row):
    rv = RegexValidator(regex="^T[0-9]$", message="Record type format incorrect.", code="invalid")
    rv(row)
    