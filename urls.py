from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls import (
handler400, handler403, handler404, handler500
)

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.signout, name='signout'),
    path('rooms', views.rooms, name='rooms'),
    path('addrooms', views.addrooms, name='addrooms'),
    path('students', views.students, name='students'),
    path('rooms/<str:roomname>/', views.room_detail, name='room_detail'),
    path('rooms/<str:roomname>/delete/', views.delete_room, name='delete_room'),
    path('add_student/', views.add_student, name='add_student'),
    path('students/<int:student_id>/', views.student_profile, name='student_profile'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('take_attendance/', views.take_attendance, name='take_attendance'),
    path('paymentinfo', views.paymentinfo, name='paymentinfo'),
    path('record_payment', views.record_payment, name='record_payment'),
    path('record_payment_profile/<int:student_id>/', views.record_payment_profile, name='record_payment_profile'),
    path('rooms/<str:roomname>/record_attendance/', views.record_attendance, name='record_attendance'),
    path('students/<int:student_id>/<int:payment_id>/', views.edit_payment_profile, name='edit_payment_profile'),
    path('bulk-upload/', views.bulk_upload_students, name='bulk_upload'),
    path('bulk-upload/success/', views.bulk_upload_success, name='bulk_upload_success'),
    path('paymentinfo/<int:payment_id>/', views.paymentinfodelete, name='paymentinfodelete'),
    path('rooms/<str:roomname>/edit_attendance', views.edit_attendance, name='edit_attendance'),
    path('saveeditattendance/<str:roomname>/<str:date>', views.saveeditattendance, name='saveeditattendance'),

    

   
    # Add more URL patterns as neededz
]