"""Check if user is authorized."""
import logging
import os

from rest_framework import mixins, viewsets
import boto3
from ..users.permissions import CanUploadReport

from ..users.permissions import IsUserOrReadOnly
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
            "signed_url":PresignedUrlInputSerializer,
        }.get(self.action, ReportFileSerializer)

    @action(methods=["POST"], detail=False)
    def signed_url(self, request,pk=None):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name= os.environ["AWS_REGION_NAME"])

        serializer = self.get_serializer(
            request.data,)

        return Response({
            "signed_url":s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': os.environ["AWS_BUCKET"],
                    'Key': serializer.data['file_name'],
                }, ExpiresIn=500)})
