# Generated by Django 5.0.3 on 2024-03-31 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_rooms'),
    ]

    operations = [
        migrations.AddField(
            model_name='rooms',
            name='roomimage',
            field=models.ImageField(default='default_room_image.jpg', upload_to='uploads/'),
        ),
    ]