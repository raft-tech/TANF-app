# Generated by Django 3.2.15 on 2024-03-05 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0010_datafilesummary_record_counts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parsererror',
            name='row_number',
            field=models.IntegerField(null=True),
        ),
    ]
