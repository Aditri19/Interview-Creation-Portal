# Generated by Django 4.1.7 on 2023-02-23 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_participant_availabilities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]