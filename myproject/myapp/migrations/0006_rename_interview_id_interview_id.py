# Generated by Django 4.1.7 on 2023-02-23 06:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_interview_interview_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interview',
            old_name='interview_id',
            new_name='id',
        ),
    ]