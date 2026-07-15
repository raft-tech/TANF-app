from django.db import migrations


PROGRAMS = {
    'tanf': {
        'name': 'TANF',
        'sections': [
            'Active Case Data',
            'Closed Case Data',
            'Aggregate Data',
            'Stratum Data',
        ],
    },
    'ssp': {
        'name': 'SSP',
        'sections': [
            'Active Case Data',
            'Closed Case Data',
            'Aggregate Data',
            'Stratum Data',
        ],
    },
    'tribal': {
        'name': 'Tribal TANF',
        'sections': [
            'Active Case Data',
            'Closed Case Data',
            'Aggregate Data',
            'Stratum Data',
        ],
    },
    'fra': {
        'name': 'FRA',
        'sections': [
            'Work Outcomes of TANF Exiters',
            'Secondary School Attainment',
            'Supplemental Work Outcomes',
        ],
    },
}


def seed_programs_and_sections(apps):
    Program = apps.get_model('stts', 'Program')
    Section = apps.get_model('stts', 'Section')

    programs = {}
    for slug, data in PROGRAMS.items():
        program, _ = Program.objects.get_or_create(
            slug=slug, defaults={'name': data['name']}
        )
        programs[slug] = program
        for section_name in data['sections']:
            Section.objects.get_or_create(program=program, name=section_name)

    return programs


def populate_ssp_program_participation(apps, schema_editor):
    STT = apps.get_model('stts', 'STT')
    SttProgramParticipation = apps.get_model('stts', 'SttProgramParticipation')

    ssp_program = seed_programs_and_sections(apps)['ssp']

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
    Section = apps.get_model('stts', 'Section')
    SttProgramParticipation = apps.get_model('stts', 'SttProgramParticipation')

    ssp_program = Program.objects.filter(slug='ssp').first()
    if ssp_program:
        SttProgramParticipation.objects.filter(
            program=ssp_program, status='ACTIVE'
        ).delete()

    for slug in PROGRAMS:
        program = Program.objects.filter(slug=slug).first()
        if not program:
            continue
        Section.objects.filter(
            program=program, name__in=PROGRAMS[slug]['sections']
        ).delete()
        if not SttProgramParticipation.objects.filter(program=program).exists():
            program.delete()


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
