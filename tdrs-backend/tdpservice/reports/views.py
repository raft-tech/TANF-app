"""Check if user is authorized."""
import logging

from django.conf import settings
from rest_framework import mixins, viewsets
from rest_framework.response import Response

from ..users.permissions import CanUploadReport

import boto3

from .serializers import ReportFileSerializer, PresignedUrlInputSerializer
from .models import User

from rest_framework.decorators import action


logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ReportFileViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Report file views."""

    queryset = User.objects.select_related("stt")

    def get_permissions(self):
        """Get permissions for the viewset."""
        permission_classes = {
            "create": [CanUploadReport],
            "signed_url": [CanUploadReport]
        }.get(self.action)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "create": ReportFileSerializer,
            "signed_url": PresignedUrlInputSerializer,
        }.get(self.action, ReportFileSerializer)

    @action(methods=["POST"], detail=False)
    def signed_url(self, request, pk=None):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME)

        serializer = self.get_serializer(
            request.data,)

        s3_params = {
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': serializer.data['file_name'],
        }

        if serializer.data['client_method'] == 'put_object':
            s3_params['ContentType'] = serializer.data['file_type']

        return Response({
            "signed_url":s3_client.generate_presigned_url(
                serializer.data['client_method'],
                Params=s3_params, ExpiresIn=500)
        })
