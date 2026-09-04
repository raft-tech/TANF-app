"""Define API views for reports app."""

from wsgiref.util import FileWrapper

from django.http import FileResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tdpservice.reports.models import ReportFile, ReportSource
from tdpservice.reports.serializers import ReportFileSerializer, ReportSourceSerializer
from tdpservice.reports.tasks import process_report_source
from tdpservice.users.permissions import (
    IsApprovedPermission,
    ReportFileDownloadTrackingPermission,
    ReportFilePermissions,
    ReportSourcePermissions,
)


class ReportFileViewSet(ModelViewSet):
    """Report file views."""

    http_method_names = ["get", "post", "head"]
    queryset = (
        ReportFile.objects.all()
        .order_by("-created_at")
        .select_related("stt", "user", "source")
    )
    serializer_class = ReportFileSerializer
    permission_classes = [ReportFilePermissions, IsApprovedPermission]

    def get_queryset(self):
        """Filter reports by STT for Data Analysts and optionally by year."""
        queryset = super().get_queryset()

        # Data Analysts should only see reports for their assigned STT
        if self.request.user.is_data_analyst and hasattr(self.request.user, "stt"):
            queryset = queryset.filter(stt=self.request.user.stt)

        # Regional Staff should only see reports for STTs in their region
        if self.request.user.is_regional_staff and hasattr(
            self.request.user, "regions"
        ):
            user_regions = self.request.user.regions.all()
            queryset = queryset.filter(stt__region__in=user_regions)

        # Query params for adding additional filters to queryset
        year = self.request.query_params.get('year')
        latest = self.request.query_params.get('latest')
        stt = self.request.query_params.get('stt')
        report_type = self.request.query_params.get('report_type')

        if stt:
            queryset = queryset.filter(stt_id=stt)
        if year:
            queryset = queryset.filter(year=year)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if latest and latest.lower() == 'true':
            queryset = queryset.order_by('-created_at')[:1]

        return queryset

    def get_serializer_context(self):
        """Retrieve additional context required by serializer."""
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        """Retrieve a file from s3 then stream it to the client."""
        obj = self.get_object()
        return FileResponse(FileWrapper(obj.file), filename=obj.original_filename)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=[
            ReportFileDownloadTrackingPermission,
            IsApprovedPermission,
        ],
    )
    def downloaded(self, request, pk=None):
        """Record the first successful download for a report file's STT."""
        if request.data:
            return Response(
                {"detail": "Request body must be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report_file = self.get_object()
        ReportFile.objects.filter(
            pk=report_file.pk,
            downloaded_at__isnull=True,
        ).update(downloaded_at=timezone.now())
        report_file.refresh_from_db(fields=["downloaded_at"])

        return Response({"downloaded_at": report_file.downloaded_at})


class ReportSourceViewSet(ModelViewSet):
    """Report source views for batch uploading report files."""

    http_method_names = ["get", "post", "head", "options"]
    queryset = ReportSource.objects.all().order_by("-created_at")
    serializer_class = ReportSourceSerializer
    permission_classes = [ReportSourcePermissions, IsApprovedPermission]

    def get_queryset(self):
        """Filter report sources by year and/or report_type if provided."""
        queryset = super().get_queryset()

        # Query params for filtering
        year = self.request.query_params.get('year')
        report_type = self.request.query_params.get('report_type')

        if year:
            queryset = queryset.filter(year=year)
        if report_type:
            queryset = queryset.filter(report_type=report_type)

        return queryset

    def get_serializer_context(self):
        """Retrieve additional context required by serializer."""
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def create(self, request, *args, **kwargs):
        """Create a new report source and trigger async processing."""
        response = super().create(request, *args, **kwargs)

        # Process the report source zip file
        process_report_source.delay(response.data.get("id"))

        return response
