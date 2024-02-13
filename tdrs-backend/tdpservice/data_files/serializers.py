"""Serialize stt data."""
import logging
from rest_framework import serializers
import base64
from io import BytesIO
import xlsxwriter
import calendar
from tdpservice.parsers.models import ParserError
from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.validators import (
    validate_file_extension,
    validate_file_infection,
)
from tdpservice.security.models import ClamAVFileScan
from tdpservice.stts.models import STT
from tdpservice.users.models import User
from tdpservice.parsers.serializers import DataFileSummarySerializer
logger = logging.getLogger(__name__)

class DataFileSerializer(serializers.ModelSerializer):
    """Serializer for Data files."""

    file = serializers.FileField(write_only=True)
    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    ssp = serializers.BooleanField(write_only=True)
    has_error = serializers.SerializerMethodField()
    summary = DataFileSummarySerializer(many=False, read_only=True)

    class Meta:
        """Metadata."""

        model = DataFile
        fields = [
            "file",
            "id",
            "original_filename",
            "slug",
            "extension",
            "user",
            "stt",
            "year",
            "quarter",
            "section",
            "created_at",
            "ssp",
            "submitted_by",
            'version',
            's3_location',
            's3_versioning_id',
            'has_error',
            'summary'
        ]

        read_only_fields = ("version",)

    def get_has_error(self, obj):
        """Return whether the file has an error."""
        parser_errors = ParserError.objects.filter(file=obj.id)
        return len(parser_errors) > 0

    def create(self, validated_data):
        """Create a new entry with a new version number."""
        ssp = validated_data.pop('ssp')
        if ssp:
            validated_data['section'] = 'SSP ' + validated_data['section']
        if validated_data.get('stt').type == 'tribe':
            validated_data['section'] = 'Tribal ' + validated_data['section']
        data_file = DataFile.create_new_version(validated_data)
        # Determine the matching ClamAVFileScan for this DataFile.
        av_scan = ClamAVFileScan.objects.filter(
            file_name=data_file.original_filename,
            uploaded_by=data_file.user
        ).last()

        # Link the newly created DataFile to the relevant ClamAVFileScan.
        if av_scan is not None:
            av_scan.data_file = data_file
            av_scan.save()

        return data_file

    def update(self, instance, validated_data):
        """Throw an error if a user tries to update a data_file."""
        raise ImmutabilityError(instance, validated_data)

    def validate_file(self, file):
        """Perform all validation steps on a given file."""
        user = self.context.get('user')
        validate_file_extension(file.name)
        validate_file_infection(file, file.name, user)
        return file


def get_xls_serialized_file(data):
    """Return xls file created from the error."""

    def chk(x):
        """Check if fields_json is not None."""
        x['fields_json'] = x['fields_json'] if x.get('fields_json', None) else {
            'friendly_name': {
                x['field_name']: x['field_name']
            },
        }
        x['fields_json']['friendly_name'] = x['fields_json']['friendly_name'] if x['fields_json'].get(
            'friendly_name', None) else {
            x['field_name']: x['field_name']
        }
        if None in x['fields_json']['friendly_name'].keys():
            x['fields_json']['friendly_name'].pop(None)
        if None in x['fields_json']['friendly_name'].values():
            x['fields_json']['friendly_name'].pop()
        return x

    def format_error_msg(x):
        """Format error message."""
        error_msg = x['error_message']
        for key, value in x['fields_json']['friendly_name'].items():
            error_msg = error_msg.replace(key, value) if value else error_msg
        return error_msg

    row, col = 0, 0
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    report_columns = [
        ('case_number', lambda x: x['case_number']),
        ('year', lambda x: str(x['rpt_month_year'])[0:4] if x['rpt_month_year'] else None),
        ('month', lambda x: calendar.month_name[
            int(str(x['rpt_month_year'])[4:])
            ] if x['rpt_month_year'] else None),
        ('error_type', lambda x: x['error_type']),
        ('error_message', lambda x: format_error_msg(chk(x))),
        ('item_number', lambda x: x['item_number']),
        ('item_name', lambda x: ','.join([i for i in chk(x)['fields_json']['friendly_name'].values()])),
        ('internal_variable_name', lambda x: ','.join([i for i in chk(x)['fields_json']['friendly_name'].keys()])),
        ('row_number', lambda x: x['row_number']),
        ('column_number', lambda x: x['column_number'])
    ]

    # write beta banner
    worksheet.write(row, col,
                    "Error reporting in TDP is still in development." +
                    "We'll be in touch when it's ready to use!" +
                    "For now please refer to the reports you receive via email")
    row, col = 2, 0
    # write csv header
    bold = workbook.add_format({'bold': True})

    def format_header(header_list: list):
        """Format header."""
        return ' '.join([i.capitalize() for i in header_list.split('_')])

    # We will write the headers in the first row
    [worksheet.write(row, col, format_header(key[0]), bold) for col, key in enumerate(report_columns)]

    [
        worksheet.write(row + 3, col, key[1](data_i)) for col, key in enumerate(report_columns)
        for row, data_i in enumerate(data)
    ]

    # autofit all columns except for the first one
    worksheet.autofit()
    worksheet.set_column(0, 0, 20)

    workbook.close()
    return {"data": data, "xls_report": base64.b64encode(output.getvalue()).decode("utf-8")}

