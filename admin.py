from django.contrib import admin
from home.models import *
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Rooms)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Payment)
