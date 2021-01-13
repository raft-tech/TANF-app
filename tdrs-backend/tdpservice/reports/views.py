"""Check if user is authorized."""
import logging
import os

from django.conf import settings
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

import boto3

from ..users.permissions import IsUser
from .serializers import ReportFileSerializer,PresignedUrlInputSerializer
from .models import ReportFile
from .models import User

from rest_framework.decorators import action

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def to_space_case(snake_str): return ''.join(x.title()+" " for x in snake_str.split('_')).strip()

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

class GetReport(APIView):
    "Get latest version of specified report file"

    query_string = False
    pattern_name = "report"
    permission_classes = [AllowAny]

    def get(self,request,year,quarter,section):
        print({"year":year,"quarter":quarter,"section":to_space_case(section),"stt":request.user.stt.id})

        print(ReportFileSerializer(ReportFile.objects.all()[0]).data)

        latest = ReportFile.find_latest_version(
            year=year,
            quarter=quarter,
            section=to_space_case(section),
            stt=request.user.stt.id)
        print(latest)
        serializer =   ReportFileSerializer(latest)
        print(serializer)
        data = serializer.data
        return Response(data,template_name="report.json")

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
            permission_classes = [IsUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "create": ReportFileSerializer,
            "signed_url":PresignedUrlInputSerializer,
        }.get(self.action, ReportFileSerializer)

    @action(methods=["POST"], detail=False)
    def signed_url(self, request,pk=None):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME)

        serializer = self.get_serializer(
            request.data,)

        return Response({
            "signed_url":s3_client.generate_presigned_url(
            serializer.data['client_method'],
            Params={
                'Bucket': os.environ["AWS_BUCKET"],
                'Key': serializer.data['file_name'],
                'ContentType': serializer.data['file_type']
            }, ExpiresIn=500)
        })
