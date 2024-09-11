"""Admin class for DataFile objects."""
from django.contrib import admin
from tdpservice.core.utils import ReadOnlyAdminMixin
from tdpservice.data_files.models import DataFile, LegacyFileTransfer
from tdpservice.parsers.models import DataFileSummary, ParserError
from tdpservice.data_files.admin.filters import DataFileSummaryPrgTypeFilter, LatestReparseEvent
from django.conf import settings
from django.utils.html import format_html
from django.core.management import call_command

DOMAIN = settings.FRONTEND_BASE_URL


class DataFileInline(admin.TabularInline):
    """Inline model for many to many relationship."""

    model = DataFile.reparse_meta_models.through
    can_delete = False
    ordering = ["-pk"]

    def has_change_permission(self, request, obj=None):
        """Read only permissions."""
        return False

@admin.register(DataFile)
class DataFileAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for DataFile models."""

    actions = ['reparse_cmd']

    #@admin.action(description="Reparse selected data files")
    def reparse_cmd(self, request, queryset):
        """Reparse the selected data files."""
        if request.POST.get('post'):
            files = queryset.values_list("id", flat=True)
            self.message_user(request, f"Reparse command has been sent to the Celery queue for {len(files)} data files.")
            from django.http import HttpResponseRedirect
            return None
            #return HttpResponseRedirect(request.get_full_path())
            #call_command("clean_and_reparse", f'-f {",".join(map(str, files))}')
            #modeladmin.message_user(request, "Data files reparse command has been sent to the Celery queue."
            self.message_user(request, "Data files reparse command has been sent to the Celery queue.")
            from django.shortcuts import redirect
            from django.urls import reverse
            url = reverse('admin:search_indexes_reparsemeta_changelist')
            return redirect(url)
        else:
            request.current_app = self.admin_site.name
            from django.template.response import TemplateResponse
            return TemplateResponse(request, "admin/action_confirmation.html")

    # TODO: add tests for this method
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.groups.filter(
            name__in=["OFA System Admin", "OFA Admin"]
            ).exists():
            if "reparse_cmd" in actions:
                del actions["reparse_cmd"]
        return actions

    def status(self, obj):
        """Return the status of the data file summary."""
        return DataFileSummary.objects.get(datafile=obj).status

    def case_totals(self, obj):
        """Return the case totals."""
        return DataFileSummary.objects.get(datafile=obj).case_aggregates

    def error_report_link(self, obj):
        """Return the link to the error report."""
        pe_len = ParserError.objects.filter(file=obj).count()

        filtered_parserror_list_url = f'{DOMAIN}/admin/parsers/parsererror/?file=' + str(obj.id)
        # have to find the error id from obj
        return format_html("<a href='{url}'>{field}</a>",
                           field="Parser Errors: " + str(pe_len),
                           url=filtered_parserror_list_url)

    error_report_link.allow_tags = True

    def data_file_summary(self, obj):
        """Return the data file summary."""
        df = DataFileSummary.objects.get(datafile=obj)
        return format_html("<a href='{url}'>{field}</a>",
                           field=f'{df.id}' + ":" + df.get_status(),
                           url=f"{DOMAIN}/admin/parsers/datafilesummary/{df.id}/change/")

    inlines = [DataFileInline]

    list_display = [
        'id',
        'stt',
        'year',
        'quarter',
        'section',
        'version',
        'data_file_summary',
        'error_report_link',
    ]

    list_filter = [
        'quarter',
        'section',
        'stt',
        'user',
        'year',
        'version',
        'summary__status',
        DataFileSummaryPrgTypeFilter,
        LatestReparseEvent
    ]

@admin.register(LegacyFileTransfer)
class LegacyFileTransferAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for LegacyFileTransfer models."""

    list_display = [
        'id',
        'sent_at',
        'result',
        'uploaded_by',
        'file_name',
        'file_shasum',
    ]

    list_filter = [
        'sent_at',
        'result',
        'uploaded_by',
        'file_name',
        'file_shasum',
    ]
