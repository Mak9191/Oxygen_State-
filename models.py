from django.db import models
from re import T
from typing import Match
# from django.db.models.enums import Choices
from django.contrib.auth.models import *
from django.utils.text import slugify
from django.urls import reverse
import datetime
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    owner_name=models.CharField(default='' ,max_length=200, blank=True)
    school_name=models.CharField(default='' ,max_length=200, blank=True)
    address= models.TextField(default='', blank=True)
    phone= models.CharField(max_length=15, default='', blank=True)

    def __str__(self):
        return self.owner_name



class Rooms(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roomname = models.CharField(max_length=50)
    room_amount = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    roomimagenumber = models.IntegerField(default=1)

    def __str__(self):
        return self.roomname

    def save(self, *args, **kwargs):
        # Check if the instance is being created for the first time
        if not self.pk:
            # Generate a random number between 1 and 5
            self.roomimagenumber = random.randint(1, 5)
        
        # Call the original save method
        super(Rooms, self).save(*args, **kwargs)



class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    rooms = models.ManyToManyField(Rooms, blank=True)
    email = models.EmailField(default='', blank=True)
    auto_assign_all_rooms = models.BooleanField(default=False)
    school = models.CharField(max_length=100, default='', blank=True)
    class_level = models.CharField(max_length=10, default='', blank=True)
    phone_number = models.CharField(max_length=15, default='')
    father_name = models.CharField(max_length=100, default='', blank=True)
    father_phone = models.CharField(max_length=15, default='', blank=True)
    mother_name = models.CharField(max_length=100, default='', blank=True)
    mother_phone = models.CharField(max_length=15, default='', blank=True)
    address = models.TextField(default='', blank=True)
    

    def __str__(self):
        return self.full_name






class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Link to Student model
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE)  # Link to Room model
    date = models.DateField(default=timezone.now)  # Attendance date (defaults to today)
    attended = models.BooleanField(default=False)  # True if attended, False otherwise
    reason = models.CharField(max_length=255, blank=True)  # Optional reason for absence

    def __str__(self):
        return f"{self.student.full_name} - {self.room.roomname} ({self.date}) - Attended: {self.attended}"





MONTH_CHOICES = (
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),
)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Replace with your User model
    date = models.DateField(default=timezone.now)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES, default=timezone.now().month)

    def __str__(self):
        return f"{self.student.full_name} - {self.room.roomname} - {self.amount} - ({self.date})"


