"""Register the email module with Django."""

from django.apps import AppConfig


class EmailConfig(AppConfig):
    """Email module configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tdpservice.email'
