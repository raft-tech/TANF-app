# Generated by Django 3.2.15 on 2024-10-04 12:17

from django.db import migrations


def switch_reparse_meta_through_model(apps, schema_editor):
    DataFile=apps.get_model("data_files","DataFile")
    ReparseMeta=apps.get_model("search_indexes","ReparseMeta")
    OldThru=DataFile.reparse_meta_models.through
    ReparseFileMeta=apps.get_model("data_files", "ReparseFileMeta")

    q = OldThru.objects.all()

    print(f'switching {q.count()} through models')

    for m in q:
        ReparseFileMeta.objects.create(
            data_file_id=m.datafile.pk,
            reparse_meta_id=m.reparsemeta.pk
        )
        m.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('data_files', '0015_datafile_reparses'),
    ]

    operations = [
        migrations.RunPython(
            switch_reparse_meta_through_model,
        ),
        migrations.RemoveField(
            model_name='datafile',
            name='reparse_meta_models',
        ),
    ]
