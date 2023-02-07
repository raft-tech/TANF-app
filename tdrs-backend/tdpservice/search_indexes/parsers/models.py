"""Models representing parser error."""

from django.db import models

class ParserError(models.Model):
    """Model representing a parser error."""

    class Meta:
        """Meta for ParserError."""

        db_table = "parser_error"

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="parser_errors",
        null=True,
    )
    file = models.ForeignKey(
        "data_files.DataFile",
        on_delete=models.CASCADE,
        related_name="parser_errors",
        null=True,
    )
    row_number = models.IntegerField()
    column_number = models.IntegerField()
    error_message = models.TextField()
    error_type = models.TextField()         # out of range, pre-parsing, etc.
    #error_context = models.TextField()
    item_number = models.IntegerField()
    field_name = models.TextField()

    def __repr__(self):
        """Return a string representation of the model."""
        return f"ParserError {self.id}"

    def __str__(self):
        """Return a string representation of the model."""
        return f"ParserError {self.id}"

    def _get_error_message(self):
        """Return the error message."""
        return self.error_message

    def _get_json_representation(self):
        """Return a JSON representation of the model."""
        return {
            "id": self.id,
            "user": self.user,
            "file": self.file,
            "row_number": self.row_number,
            "column_number": self.column_number,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "item_number": self.item_number,
            "field_name": self.field_name,
        }