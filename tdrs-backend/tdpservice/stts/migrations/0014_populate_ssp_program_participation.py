from django.db import migrations


def populate_ssp_program_participation(apps, schema_editor):
    Program = apps.get_model('stts', 'Program')
    STT = apps.get_model('stts', 'STT')
    SttProgramParticipation = apps.get_model('stts', 'SttProgramParticipation')

    ssp_program, _ = Program.objects.get_or_create(slug='ssp', defaults={'name': 'SSP'})

    participation_rows = [
        SttProgramParticipation(
            stt=stt,
            program=ssp_program,
            status='ACTIVE',
        )
        for stt in STT.objects.filter(ssp=True)
        if not SttProgramParticipation.objects.filter(
            stt=stt, program=ssp_program
        ).exists()
    ]

    SttProgramParticipation.objects.bulk_create(participation_rows)


def reverse_ssp_program_participation(apps, schema_editor):
    Program = apps.get_model('stts', 'Program')
    SttProgramParticipation = apps.get_model('stts', 'SttProgramParticipation')

    ssp_program = Program.objects.filter(slug='ssp').first()
    if not ssp_program:
        return

    SttProgramParticipation.objects.filter(program=ssp_program, status='ACTIVE').delete()
    if not SttProgramParticipation.objects.filter(program=ssp_program).exists():
        ssp_program.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('stts', '0013_program_section_sttprogramparticipation'),
    ]

    operations = [
        migrations.RunPython(
            populate_ssp_program_participation,
            reverse_ssp_program_participation,
        ),
    ]
