# Generated by Django 5.0.3 on 2024-04-02 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_rooms_roomimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rooms',
            name='roomimage',
        ),
        migrations.AddField(
            model_name='rooms',
            name='roomimagenumber',
            field=models.IntegerField(default=1),
        ),
    ]