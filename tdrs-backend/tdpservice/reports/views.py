"""Check if user is authorized."""
import logging

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import mixins, viewsets
from django.middleware import csrf
from django.utils import timezone
from .serializers import ReportFileSerializer
from .models import User

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# class AuthorizationCheck(APIView):
#     """Check if user is authorized."""

#     query_string = True
#     pattern_name = "authorization-check"
#     permission_classes = [AllowAny] # What should I set this to?

#     def post(self, request, *args, **kwargs):
#         """Handle get request and verify user is authorized."""
#         user = request.user
#         serializer = ReportFileSerializer(request.data)
#         if user.is_authenticated:
#             logger.info(
#                 "Auth check PASS for user: %s on %s", user.username, timezone.now()
#             )
#             res = Response({"success":True})
#             res['Access-Control-Allow-Headers'] = "X-CSRFToken"
#             return res
#         else:
#             logger.info("Auth check FAIL for user on %s", timezone.now())
#             return Response({"authenticated": False})


class ReportFileViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Report file views"""

    queryset = User.objects.select_related("stt")

    def get_permissions(self):
        """Get permissions for the viewset."""
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsUserOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "create": ReportFileSerializer,
        }.get(self.action, ReportFileSerializer)
