# Generated by Django 3.2.11 on 2022-03-10 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_alter_user_hhs_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='nextgen_xid',
            field=models.UUIDField(blank=True, editable=False, null=True, unique=True),
        ),
    ]
