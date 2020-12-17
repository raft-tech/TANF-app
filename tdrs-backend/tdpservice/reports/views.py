"""Check if user is authorized."""
import logging

from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from ..users.permissions import IsUserOrReadOnly
from .serializers import ReportFileSerializer,PresignedUrlInputSerializer
from .models import User
import boto3
from botocore.exceptions import ClientError

from rest_framework.decorators import action

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
    """Report file views."""

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
            "get_signed_url":PresignedUrlInputSerializer,
        }.get(self.action, ReportFileSerializer)

    @action(methods=["POST"], detail=False)
    def get_signed_url(self, request,pk=None):
        s3_client = boto3.client('s3')
        serializer = self.get_serializer(
            self.request.user,
            request.data,
        )
        try:
            Response(s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': "cg-f0e35234-e70c-491c-a044-6836dd6abd59",
                    'Region' : "us-gov-west-1",
                    'Key': serializer.data['file_name'],
                }, ExpiresIn=500))
        except ClientError as e:
            logging.error(e)
            return None
