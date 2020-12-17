"""Check if user is authorized."""
import logging

from rest_framework import mixins, viewsets

from ..users.permissions import CanUploadReport
from .models import User
from .serializers import ReportFileSerializer
from .models import User
from .serializers import ReportFileSerializer

from rest_framework.decorators import action

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ReportFileViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet,
):
    """Report file views."""

    queryset = User.objects.select_related("stt")

    def get_permissions(self):
        """Get permissions for the viewset."""
        permission_classes = {"create": [CanUploadReport]}.get(self.action)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {"create": ReportFileSerializer, }.get(self.action, ReportFileSerializer)

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
