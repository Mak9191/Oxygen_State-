from pyexpat import model
from django.forms import *
from django import forms
from home.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    username = forms.CharField(label='username', min_length=5, max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)  
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)  
    
    def username_clean(self):  
        username = self.cleaned_data['username'].lower()  
        new = User.objects.filter(username = username)  
        if new.count():  
            raise ValidationError("User Already Exist")  
        return username  
  
    def email_clean(self):  
        email = self.cleaned_data['email'].lower()  
        new = User.objects.filter(email=email)  
        if new.count():  
            raise ValidationError(" Email Already Exist")  
        return email  
  
    def clean_password2(self):  
        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  
  
        if password1 and password2 and password1 != password2:  
            raise ValidationError("Password don't match")  
        return password2  
    '''
    def save(self, commit = True):  
        user = User.objects.create_user(  
            self.cleaned_data['username'],  
            self.cleaned_data['email'],  
            self.cleaned_data['password1']  
        )  
        return user  
    '''
    
  
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }



class AddroomForms(ModelForm):
    class Meta:
        model = Rooms
        fields = ('roomname', 'room_amount')


class StudentForm(forms.ModelForm):
    rooms = forms.ModelMultipleChoiceField(queryset=Rooms.objects.all(), required=False)
    class Meta:
        model = Student
        fields = ('full_name', 'phone_number', 'rooms')

class StudentEditForm(forms.ModelForm):
    rooms = forms.ModelMultipleChoiceField(queryset=Rooms.objects.all(), widget=forms.SelectMultiple, required=False)
    class Meta:
        model = Student
        fields = ['full_name', 'phone_number', 'rooms', 'email', 'school', 'class_level', 'father_name', 'father_phone', 'mother_name', 'mother_phone', 'address']

class TakeAttendanceForm(forms.Form):
    rooms = forms.ModelChoiceField(queryset=Rooms.objects.all(), label='Select Room')
    def __init__(self, students, *args, **kwargs):
        super(TakeAttendanceForm, self).__init__(*args, **kwargs)
        for student in students:
            self.fields[f'student_{student.id}'] = forms.BooleanField(label=student.full_name, required=False)
        


class PaymentForm(forms.ModelForm):
    room = forms.ModelChoiceField(queryset=Rooms.objects.all(), label='Select Room')
    class Meta:
        model = Payment
        fields = ['student', 'room', 'amount', 'month', 'date']

class PaymentFormProfile(forms.ModelForm):
    room = forms.ModelChoiceField(queryset=Rooms.objects.all(), label='Select Room')
    class Meta:
        model = Payment
        fields = ['room', 'amount', 'month', 'date']


class EditPaymentFromProfile(forms.ModelForm):
    room = forms.ModelChoiceField(queryset=Rooms.objects.all(), label='Select Room')
    class Meta:
        model = Payment
        fields = ['room', 'amount', 'month', 'date']




class PaymentFilterFormRoom(forms.Form):
    room = forms.ModelChoiceField(queryset=Rooms.objects.all(), empty_label="All Rooms", required=False)
    month = forms.ChoiceField(choices=MONTH_CHOICES, required=False)


class RecordAttendance(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'room', 'attended', 'date']




def validate_file_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Only CSV files are allowed.')

class BulkUploadForm(forms.Form):
    file = forms.FileField(validators=[validate_file_extension])
