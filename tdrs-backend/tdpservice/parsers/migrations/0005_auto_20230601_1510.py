# Generated by Django 3.2.15 on 2023-06-01 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0004_parsererror_object_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parsererror',
            name='object_id',
        ),
        migrations.RenameField(
            model_name='parsererror',
            old_name='object_uuid',
            new_name='object_id',
        ),
    ]
