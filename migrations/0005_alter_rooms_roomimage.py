# Generated by Django 5.0.3 on 2024-03-31 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_alter_rooms_roomimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rooms',
            name='roomimage',
            field=models.ImageField(default='defaultassets/images/default_room_image.png', upload_to='uploads/'),
        ),
    ]
