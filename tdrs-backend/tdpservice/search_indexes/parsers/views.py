from rest_framework.viewsets import ModelViewSet
from .serializers import ParsingErrorSerializer
from .models import ParserError

class ParsingErrorViewSet(ModelViewSet):
    """Data file views."""

    queryset = ParserError.objects.all()
    serializer_class = ParsingErrorSerializer