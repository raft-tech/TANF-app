# Generated by Django 3.2.15 on 2023-03-06 14:34

from django.db import migrations, models
import logging

logger = logging.getLogger()


def migrate_location_id_to_stt_or_region(apps, schema_editor):
    User = apps.get_model('users', 'User')
    STT = apps.get_model('stts', 'STT')
    Region = apps.get_model('stts', 'Region')

    logger.info('migrating user location_id to region/stt')

    for user in User.objects.all():

        if user.location_id and user.location_type:
            if user.location_type.model == 'stt':
                try:
                    user.stt = STT.objects.get(pk=user.location_id)
                except STT.DoesNotExist:
                    logger.error(f'no stt with id {user.location_id}')
            elif user.location_type.model == 'region':
                try:
                    user.region = Region.objects.get(pk=user.location_id)
                except Region.DoesNotExist:
                    logger.error(f'no region with id {user.location_id}')

            user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_auto_20230306_1431'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(migrate_location_id_to_stt_or_region)
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='user',
                    name='location_id',
                ),
                migrations.RemoveField(
                    model_name='user',
                    name='location_type'
                )
            ]
        )
    ]
