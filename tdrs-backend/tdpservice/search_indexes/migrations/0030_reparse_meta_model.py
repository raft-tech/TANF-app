# Generated by Django 3.2.15 on 2024-08-01 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_indexes', '0029_tanf_tribal_ssp_alter_verbose_names'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReparseMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('finished', models.BooleanField(default=False)),
                ('num_files_to_reparse', models.PositiveIntegerField(default=0)),
                ('files_completed', models.PositiveIntegerField(default=0)),
                ('files_failed', models.PositiveIntegerField(default=0)),
                ('num_records_deleted', models.PositiveIntegerField(default=0)),
                ('num_records_created', models.PositiveIntegerField(default=0)),
                ('total_num_records_initial', models.PositiveBigIntegerField(default=0)),
                ('total_num_records_post', models.PositiveBigIntegerField(default=0)),
                ('db_backup_location', models.CharField(max_length=512)),
                ('fiscal_quarter', models.CharField(max_length=2, null=True)),
                ('fiscal_year', models.PositiveIntegerField(null=True)),
                ('all', models.BooleanField(default=False)),
                ('new_indices', models.BooleanField(default=False)),
                ('delete_old_indices', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Re-parse Meta',
            },
        ),
    ]
