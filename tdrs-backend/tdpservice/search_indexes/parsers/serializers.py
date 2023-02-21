from rest_framework import serializers
from .models import ParserError


class ParsingErrorSerializer(serializers.ModelSerializer):
    """Serializer for Parsing Errors."""
    def __init__(self, *args, **kwargs):
        """Override init to filter fields based on `fields` argument that
    controls which fields should be displayed."""
        super(ParsingErrorSerializer, self).__init__(*args, **kwargs)
        fields = kwargs['context']['request'].query_params.get('fields')
        if fields is not None:
            fields = fields.split(',')
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


    class Meta:
        """Metadata."""

        model = ParserError
        fields = '__all__'
