# Generated by Django 5.0.3 on 2024-04-03 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_remove_rooms_roomimage_rooms_roomimagenumber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rooms',
            name='roomname',
            field=models.CharField(default='', max_length=50),
        ),
    ]
