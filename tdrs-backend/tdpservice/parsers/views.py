"""Views for the parsers app."""
from tdpservice.users.permissions import IsApprovedPermission
from rest_framework.viewsets import ModelViewSet
from .serializers import DataFileSummarySerializer
from .models import DataFileSummary


class DataFileSummaryViewSet(ModelViewSet):
    """DataFileSummary file views."""

    queryset = DataFileSummary.objects.all()
    serializer_class = DataFileSummarySerializer
    permission_classes = [IsApprovedPermission]
