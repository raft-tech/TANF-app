from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stts', '0012_stt_timezone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='stts.program')),
            ],
        ),
        migrations.CreateModel(
            name='SttProgramParticipation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('FORMER', 'Former'), ('NEVER', 'Never')], max_length=10)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stt_participations', to='stts.program')),
                ('sections', models.ManyToManyField(blank=True, related_name='participations', to='stts.section')),
                ('stt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_participations', to='stts.stt')),
            ],
        ),
        migrations.AddConstraint(
            model_name='section',
            constraint=models.UniqueConstraint(fields=('program', 'name'), name='section_uniq_program_name'),
        ),
        migrations.AddConstraint(
            model_name='sttprogramparticipation',
            constraint=models.UniqueConstraint(fields=('stt', 'program'), name='participation_uniq_stt_program'),
        ),
    ]
