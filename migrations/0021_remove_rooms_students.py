# Generated by Django 5.0.3 on 2024-04-06 14:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_rooms_students'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rooms',
            name='students',
        ),
    ]