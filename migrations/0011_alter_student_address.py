# Generated by Django 5.0.3 on 2024-04-04 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_alter_student_class_level_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='address',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
