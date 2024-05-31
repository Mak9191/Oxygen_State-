# Generated by Django 5.0.3 on 2024-04-10 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0024_rooms_room_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rooms',
            name='room_amount',
            field=models.DecimalField(decimal_places=2, default='0.00', max_digits=10),
        ),
    ]
