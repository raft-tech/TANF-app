"""Define API views for report files"""
import logging

from django.utils import timezone

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Report
from .permissions import IsUserOrReadOnly
from .serializers import ReportFileSerializer

logger = logging.getLogger(__name__)


class ReportViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "create": CreateUserSerializer,
            "set_profile": UserProfileSerializer,
        }.get(self.action, ReportSerializer)
