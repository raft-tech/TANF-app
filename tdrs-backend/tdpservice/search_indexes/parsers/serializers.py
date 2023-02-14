from rest_framework import serializers
from .models import ParserError


class ParsingErrorSerializer(serializers.ModelSerializer):
    """Serializer for Parsing Errors."""
    class Meta:
        """Metadata."""

        model = ParserError
        fields = '__all__'