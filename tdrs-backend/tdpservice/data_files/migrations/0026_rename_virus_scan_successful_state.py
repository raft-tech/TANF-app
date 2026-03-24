from django.db import migrations, models


def rename_virus_scan_successful_to_completed(apps, schema_editor):
    DataFile = apps.get_model("data_files", "DataFile")
    DataFile.objects.filter(state="virus_scan_successful").update(
        state="virus_scan_completed"
    )


def rename_virus_scan_completed_to_successful(apps, schema_editor):
    DataFile = apps.get_model("data_files", "DataFile")
    DataFile.objects.filter(state="virus_scan_completed").update(
        state="virus_scan_successful"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("data_files", "0025_datafile_state"),
    ]

    operations = [
        migrations.RunPython(
            rename_virus_scan_successful_to_completed,
            rename_virus_scan_completed_to_successful,
        ),
        migrations.AlterField(
            model_name="datafile",
            name="state",
            field=models.CharField(
                choices=[
                    ("uploaded", "Uploaded"),
                    ("virus_scan_started", "Virus scan started"),
                    ("virus_scan_failed", "Virus scan failed"),
                    ("virus_scan_completed", "Virus scan completed"),
                    ("parse_started", "Parse started"),
                    ("parsed_with_errors", "Parsed with errors"),
                    ("parse_completed", "Parse completed"),
                    ("stuck", "Stuck"),
                    ("completed", "Completed"),
                    ("canceled", "Canceled"),
                ],
                default="uploaded",
                max_length=32,
            ),
        ),
    ]
