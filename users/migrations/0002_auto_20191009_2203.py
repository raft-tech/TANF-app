# Generated by Django 2.2.6 on 2019-10-09 22:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tanfuser',
            name='password',
        ),
        migrations.AlterField(
            model_name='tanfuser',
            name='last_login',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
