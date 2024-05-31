from django.shortcuts import render
from email.headerregistry import Address
from multiprocessing import context
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.contrib.auth.forms import *
from django.contrib.auth import authenticate, login as loginUser, logout
from home.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_control
from home.forms import *
from django.db.models import Count
from django.contrib.sites.shortcuts import get_current_site  
# from django.utils.encoding import force_text, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
# from home.token import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage  
from datetime import date, timedelta
from django.utils import timezone
import datetime
from django.db.models import Sum
import io
from xhtml2pdf import pisa
from django.db.models.functions import Lower

  

@login_required(login_url='login')
def home(request):
    user=request.user
    room= Rooms.objects.filter(user=user)
    total_rooms=room.count()
    students_list= Student.objects.filter(user=user)
    total_students=students_list.count()
    current_month = timezone.now().month
    
    # print(current_month)
    payments_current_month = Payment.objects.filter(user=user, month=current_month)
    # print(payments_current_month)
    total_payment_current_month = payments_current_month.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    print(total_payment_current_month)
    payments_this_month = Payment.objects.filter(month=current_month)

    # Dictionary to store room and student count (without payment)
    room_unpaid_counts = {}
    for room in Rooms.objects.filter(user=user):
        students_in_room = room.student_set.all()
        unpaid_students = students_in_room.exclude(payment__in=payments_this_month, payment__room=room)

        room_unpaid_counts[room.roomname] = unpaid_students.count()
    print(room_unpaid_counts)
    context={'user':user, 'room':room, 'total_rooms':total_rooms, 'current_month': current_month, 'total_students':total_students, 'total_payment_current_month':total_payment_current_month, 'room_unpaid_counts': room_unpaid_counts}
    return render(request, 'home/home.html', context)

def rooms(request):
    user=request.user
    room= Rooms.objects.filter(user=user).annotate(num_students=Count('student'))
    total_rooms=room.count()
    
    context={
        'user':user,
        'room':room, 
        'total_rooms':total_rooms, 
        
        }
    return render(request, 'home/rooms.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.method == "GET":
        form=AuthenticationForm()
        context={
            "form" : form
        }
        return render(request, 'login/login.html', context=context)

    else:
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            username= form.cleaned_data.get('username')
            password= form.cleaned_data.get('password')
            user=authenticate(username=username, password=password)
            if user is not None:
                if user.is_active==False:
                    context={
                         "form" : form,
                        "invalid": 1,
                        }

                loginUser(request,user)
                return redirect('home')


        else:
            
            context={
            "form" : form,
            "invalid": 1,
            }
            return render(request, 'login/login.html', context=context)





def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        print('post pass')
        if form.is_valid():
            print('is valid')
            user = form.save(commit=False) 
            form.save() 
            return redirect('login')  
    
    else:
        print('not post pass')
        form = SignUpForm()
    
        
    return render(request, 'login/signup.html', {'form':form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signout(request):
    logout(request)
    return redirect('login')

def addrooms(request):
    if request.user.is_authenticated:
        user= request.user
        form= AddroomForms(request.POST)
        print(user)
        if form.is_valid():
            room_name = form.cleaned_data['roomname'] 
            room_amt = form.cleaned_data['room_amount'] 

            # Check if a room with the same name already exists
            if Rooms.objects.filter(user=user, roomname=room_name).exists():
                message="Room with same name already exist"
                print('cannot add')
                return redirect('rooms')
            else:
                print(form.cleaned_data)
                adds=form.save(commit=False)
                adds.user=user
                adds.save()
                print('added')
                return redirect('rooms')
        else:
            print('unable to add')
            return redirect('rooms')


def students(request):
    user=request.user
    students_list= Student.objects.filter(user=user).order_by(Lower('full_name'))
    room= Rooms.objects.filter(user=user)
    students_count=students_list.count()
    print(students_count)
     
    context={'user':user,'students_list':students_list, 'students_count':students_count, 'room': room}
    return render(request, 'home/students.html', context)
    

from django.db.models import Min
def room_detail(request, roomname):
    current_user = request.user
    froom = get_object_or_404(Rooms, user=current_user, roomname=roomname)
    print(froom)

    ##############3
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)

    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    ################3



    today = timezone.now()
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    students_list= Student.objects.filter(user=current_user, rooms=froom).order_by('full_name')
    student_count = students_list.count()
    attendance_lists=Attendance.objects.filter(room=froom, date__range=(start_of_day, end_of_day))
    

    current_month = datetime.now().month
    students_with_payment = Payment.objects.filter(
    user=current_user,
    room=froom,
    month=current_month
    )
    assigned_students = froom.student_set.all() 
    all_students= Student.objects.filter(user=current_user).order_by('full_name')

    if request.method == 'POST':
        # Process the form for assigning students to the room
        student_ids = request.POST.getlist('students')
        students_to_assign = Student.objects.filter(id__in=student_ids)
        
        # Students currently assigned to the room
        current_assigned_students = set(assigned_students)

        # Students selected in the form
        selected_students = set(students_to_assign)

        # Find students to remove from the room
        students_to_remove = current_assigned_students - selected_students
        
        # Find students to add to the room
        students_to_add = selected_students - current_assigned_students
        
        # Remove students from the room
        for student in students_to_remove:
            student.rooms.remove(froom)
        
        # Add students to the room
        for student in students_to_add:
            student.rooms.add(froom)
        
        return redirect('room_detail', roomname=roomname)

    context = {
        'room': froom,
        'students_list': students_list,
        'student_count': student_count,
        'attendance_lists': attendance_lists, 
        'dates': dates,
        'today':today,
        'students_with_payment':students_with_payment,
        'all_students':all_students,
        'assigned_students':assigned_students,
        # 'attendance_data': attendance_data,
        # 'start_date': start_date.strftime('%Y-%m-%d'),
        # 'end_date': today.strftime('%Y-%m-%d'),
    }

    return render(request, 'home/roomdetail.html', context)

def delete_room(request, roomname):
    current_user = request.user
    room = get_object_or_404(Rooms, user=current_user, roomname=roomname)
    room.delete()
    return redirect('rooms')

def student_profile(request, student_id):
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
    current_user = request.user
    current_datetime = date.today()
    current_month = current_datetime.month
    print(current_month)
    student = get_object_or_404(Student, user=current_user, id=student_id)
    room= Rooms.objects.filter(user=current_user)
    today=date.today().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        print('1')
        if form.is_valid():
            print('2 valid')
            form.save()
            print('3')
            
            return redirect('student_profile', student_id=student.id)  # Redirect to profile after edit
        else:
            print(form.errors)
    else:
        form = StudentEditForm(instance=student) 

    
    payments = Payment.objects.filter(student_id=student_id, user=current_user)
    orderedpayments = Payment.objects.filter(student_id=student_id, user=current_user).order_by('-id')
    
    payments_by_room = Payment.objects.filter(student=student).values('room__roomname').annotate(total_payment=Sum('amount'))
    


    context = {
        'student': student,
        'room':room,
        'payments': payments,
        'payments_by_room': payments_by_room,
        'MONTH_CHOICES': MONTH_CHOICES,
        'today': today,
        'current_month': current_month,
        'orderedpayments':orderedpayments,
    }
    return render(request, 'home/student_profile.html', context)



def add_student(request):
    if request.user.is_authenticated:
        user = request.user
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)  # Don't save yet
            student.user = user
            selected_rooms = form.cleaned_data['rooms']  # Get selected rooms
            student.save()  # Save the student
            student.rooms.set(selected_rooms)  # Assign rooms to the student
            print('Student added with rooms')
            return redirect('students')
        else:
            print('Unable to add student')
            return redirect('students')



def student_detail(request, student_id):
    current_user = request.user
    student = get_object_or_404(Student, pk=student_id, user=current_user)
    

    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_detail', student_id=student.id)  # Redirect back to detail page
    else:
        form = StudentEditForm(instance=student)  # Pre-populate form

   

    return render(request, 'home/student_detail.html', {'form': form, 'student': student})




def delete_student(request, student_id):
    current_user = request.user
    student = get_object_or_404(Student, user=current_user, id=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('students') 
    return render(request, 'home/student.html', {'student': student})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def take_attendance(request, roomname):
    current_user = request.user
    froom = get_object_or_404(Rooms, user=current_user, roomname=roomname)
    students= Student.objects.filter(user=current_user, room=froom)
    content={'students':student}

    # if request.method == 'POST':
    #     form = TakeAttendanceForm(request.POST, students=Student.objects.all())
    #     if form.is_valid():
    #         selected_room = form.cleaned_data['rooms']  # Get the selected room
    #         # Create Attendance objects for students without existing records
    #         for student in Student.objects.all():
    #             attendance, created = Attendance.objects.get_or_create(student=student, date=timezone.now())
    #             if created:
    #                 attendance.attended = False
    #                 attendance.save()

    #         # Update attendance based on form data
    #         for student_id, attended in form.cleaned_data.items():
    #             if student_id.startswith('student_'):
    #                 attendance_id = student_id.split('_')[1]
    #                 attendance = Attendance.objects.get(pk=attendance_id)
    #                 attendance.attended = attended
    #                 attendance.room = selected_room  # Assign the selected room
    #                 attendance.save()

    #         message = 'Attendance saved successfully!'

    #         return render(request, 'home/record_attendence.html', {'form': form, 'message': message})

    # else:
    #     # Create a new form instance with all students and rooms as choices
    #     form = TakeAttendanceForm(students=Student.objects.all())

    return render(request, 'home/record_attendence.html', context)


def paymentinfo(request):
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
    current_user = request.user
    student = Student.objects.filter(user=current_user)
    room= Rooms.objects.filter(user=current_user)
    payments = Payment.objects.filter(user=current_user).order_by('-id')

    if request.method == 'POST':
        form = PaymentFilterFormRoom(request.POST)
        if form.is_valid():
            
            room_id = form.cleaned_data['room']
            month=form.cleaned_data['month']
            print(month)
            # Filter payments based on selected room and month
            if room_id:
                payments = payments.filter(room=room_id)
            if month:
                payments = payments.filter(month=month)
                
    else:
        form = PaymentFilterFormRoom()

    context={
        'student': student,
        'room': room,
        'payments': payments,
        'MONTH_CHOICES': MONTH_CHOICES
    }
    return render(request, 'home/payment_info.html', context)
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def paymentinfodelete(request, payment_id):
    current_user = request.user
    userprofile = get_object_or_404(UserProfile, user=current_user)  # Assuming UserProfile model exists
    try:
        existingpayment = get_object_or_404(Payment, pk=payment_id, user=current_user)
        existingpayment.delete()
    except Exception as e:
        print(f"Error deleting payment: {e}")
    return redirect('paymentinfo')


def record_payment(request):
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
    current_user = request.user
    student = Student.objects.filter(user=current_user)
    room= Rooms.objects.filter(user=current_user)
    today=date.today().strftime('%Y-%m-%d')
    if request.user.is_authenticated:
        print('authenticated')
        form = PaymentForm(request.POST)
        
        print('auto1')
        if form.is_valid():
            payment=form.save(commit=False)
            payment.user = current_user
            payment.student= form.cleaned_data['student']
            payment.room= form.cleaned_data['room']
            payment.month= form.cleaned_data['month']
            payment.amount= form.cleaned_data['amount']
            payment.date= form.cleaned_data['date']

            
            print(payment)
            payment.save()
            return redirect('paymentinfo')  # Redirect to payment information page
        else:
            print(form.errors)  
            form = PaymentForm()  
    
        
        
        return render(request, 'home/record_payment.html', {'form': form, 'student': student, 'room':room, 'MONTH_CHOICES': MONTH_CHOICES, 'today':today})





# def record_payment_profile(request, student_id):
#     current_user=request.user
#     student = get_object_or_404(Student, pk=student_id, user=current_user)
#     if request.user.is_authenticated:
#         form = PaymentFormProfile(request.POST)
#         print('check1')
#         if form.is_valid():
#             payment=form.save(commit=False)
#             payment.user = request.user
#             print('check2')
#             payment.student= student
#             print('check3')
#             payment.room= form.cleaned_data['room']
#             print('check4')
#             payment.month= form.cleaned_data['month']
#             print('check5')
#             payment.amount= form.cleaned_data['amount']
#             print('check6')
#             payment.date= form.cleaned_data['date']
#             print(payment)
        
#             payment.save()
#             return redirect('student_profile', student_id=student.id)  # Redirect to payment information page
#         else:
#             print(form.errors)
#             form = PaymentForm()  
#             return redirect('student_profile', student_id=student.id) 
    
        
        
#     return render(request, 'home/student_profile.html')

# def generate_payment_receipt_pdf(student):
#     context = {'student': student}
#     html_content = render_to_string('emails/payment_recipt.html', context)

#     result = io.BytesIO()  # Use io.BytesIO
#     pdf = pisa. pisaDocument(StringIO(html_content.encode("utf-8")), result)

#     if not pdf.err:
#         return result.getvalue()
#     else:
#         raise Exception(f"Error generating PDF: {pdf.err}")



# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from io import BytesIO

# def generate_pdf_receipt(payment):
#     # Create a canvas for PDF generation
#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=letter)

#     # Draw receipt content using ReportLab methods
#     c.drawString(100, 750, f"Payment Receipt for Student: {payment.student.full_name}")
#     c.drawString(100, 730, f"Room: {payment.room.roomname}")
#     c.drawString(100, 710, f"Amount Paid: {payment.amount}")
#     # Add more receipt details as needed

#     # Save the PDF to the buffer
#     c.showPage()
#     c.save()

#     # Return the buffer

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime

# Define left padding
LEFT_PADDING = 0.5*cm
# Define line spacing
LINE_SPACING = 0.2*cm

def generate_pdf_attachment():
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer, pagesize=A5)

    # Draw border around the entire page
    pdf_canvas.setStrokeColor(colors.black)
    pdf_canvas.rect(cm, cm, A5[0]-2*cm, A5[1]-2*cm)

    # Set text color to blue for institute name
    pdf_canvas.setFillColor(colors.blue)

    # Draw institute name with left padding
    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(cm + LEFT_PADDING, A5[1]-2*cm - LINE_SPACING, "Jyotsna's HeadStart Academy")

    # Reset text color to black
    pdf_canvas.setFillColor(colors.black)  

    # Draw address with left padding
    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.drawString(cm + LEFT_PADDING, A5[1]-3*cm - LINE_SPACING, "209, 32 Park Area, East Park Road Karol Bagh")
    pdf_canvas.drawString(cm + LEFT_PADDING, A5[1]-3.5*cm - LINE_SPACING, "New Delhi 10005")

    # Draw title with left padding
    pdf_canvas.setFont("Helvetica-Bold", 16)
    pdf_canvas.drawCentredString(A5[0]/2, A5[1]-6*cm - LINE_SPACING, "Fee Receipt")

    # Transpose data for horizontal table
    data = [
        ("Student Name:", "Amaan Khan"),
        ("Fees Paid:", "2250"),
        ("Classes:", "Math"),
        ("Month:", "April"),
        ("Payment Mode:", "Cash"),
        ("Date:", datetime.now().strftime("%Y-%m-%d")),
        ("Time:", datetime.now().strftime("%H:%M:%S"))
    ]

    # Draw table
    table_start_y = A5[1] - 9*cm - LINE_SPACING
    row_height = 0.6*cm
    col1_start_x = cm + LEFT_PADDING
    col2_start_x = cm + LEFT_PADDING + 6*cm
    for i, (label, value) in enumerate(data):
        y = table_start_y - i*row_height
        pdf_canvas.drawString(col1_start_x, y, label)
        pdf_canvas.drawString(col2_start_x, y, value)

    pdf_canvas.save()

    buffer.seek(0)
    return buffer.getvalue()






# from reportlab.lib.pagesizes import A5
# from reportlab.lib import colors
# from reportlab.lib.units import cm
# from reportlab.pdfgen import canvas
# from datetime import datetime

# def generate_pdf_attachment(payment, student, userprofile):
#     buffer = BytesIO()
#     pdf_canvas = canvas.Canvas(buffer, pagesize=A5)

#     # Draw institute name
#     pdf_canvas.setFont("Helvetica-Bold", 14)
#     pdf_canvas.drawString(cm, A5[1]-2*cm, f"{userprofile.owner_name}")
#     pdf_canvas.setFont("Helvetica-Bold", 12)
#     pdf_canvas.drawString(cm + 4*cm, A5[1]-2*cm, f"{userprofile.school_name}")

#     # Draw address
#     pdf_canvas.setFont("Helvetica", 10)
#     pdf_canvas.drawString(cm, A5[1]-3*cm, f"{userprofile.address}")

#     # Draw title
#     pdf_canvas.setFont("Helvetica-Bold", 16)
#     pdf_canvas.drawCentredString(A5[0]/2, A5[1]-6*cm, "Fee Receipt")

#     # Transpose data for horizontal table
#     data = [
#         ("Student Name:", f"{ student.full_name }"),
#         ("Fees Paid:", f"{ payment.amount}"),
#         ("Classes:", f"{ payment.room.roomname }"),
#         ("Month:", f"{ payment.month }"),
#         ("Date:", f"{ payment.date }")
#     ]

#     # Draw table
#     table_start_y = A5[1] - 9*cm
#     row_height = 0.6*cm
#     col1_start_x = cm
#     col2_start_x = 6*cm
#     for i, (label, value) in enumerate(data):
#         y = table_start_y - i*row_height
#         pdf_canvas.drawString(col1_start_x, y, label)
#         pdf_canvas.drawString(col2_start_x, y, value)

#     pdf_canvas.showPage()
#     pdf_canvas.save()

#     buffer.seek(0)
#     return buffer.getvalue()











@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def record_payment_profile(request, student_id):
    current_user = request.user
    student = get_object_or_404(Student, pk=student_id, user=current_user)
    userprofile=get_object_or_404(UserProfile, user=current_user)
    pho="+91"+" "+ student.phone_number
    print(pho)
    if request.user.is_authenticated:
        form = PaymentFormProfile(request.POST)
        
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = current_user
            payment.student = student
            payment.save()



            # Send email with PDF attachment
            # mail_subject = 'Fee receipt for payment'
            # message = render_to_string('emails/payment_recipt.html', {
            #     'student': student,
            # })
            # to_email = student.email
            # email = EmailMessage(
            #     mail_subject, message, to=[to_email]
            # )
            # email.attach('payment_recipt.pdf', pdf_content, 'application/pdf')
            # email.send()
            if 'checkstudentmail' in request.POST:
                pdf_content = generate_pdf_attachment()

                from_email = f'{userprofile.school_name} <justsubscribe.share@gmail.com>'
                mail_subject = 'Fee receipt for payment'
                message = render_to_string('emails/payment_recipt.html', {
                    'student': student,
                })
                to_email = student.email
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.attach('document.pdf', pdf_content, 'application/pdf')
                email.send()
            

            # if 'checkstudentwhatsapp' in request.POST:
            #     import pywhatkit as kit
            #     print(pho)
            #     message = "Chocolate Received 😊"
            #     print(message)
            #     kit.sendwhatmsg_instantly(pho, message)







            # from_email = 'Little Academy <justsubscribe.share@gmail.com>'
            # current_site = get_current_site(request)  
            # mail_subject = 'Fee recipt for payment' 
            # #user = get_object_or_404(User) 
            # message = render_to_string('emails/payment_recipt.html', {  
            #     'student': student, 'payment': payment
                  
            # })  
            # to_email = student.email
            # context={
            #     'cemail':to_email,
            # }  
            # email = EmailMessage(  
            #             mail_subject, message, from_email=from_email, to=[to_email]  
            # )  
            # email.send()  


            return redirect('student_profile', student_id=student.id)
        else:
            print(form.errors)
            # Re-render the profile page with the form errors
            return redirect('student_profile', student_id=student.id)
    
 
  
    

    return render(request, 'home/student_profile.html')





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_payment_profile(request, student_id, payment_id):
    current_user = request.user
    student = get_object_or_404(Student, pk=student_id, user=current_user)
    userprofile = get_object_or_404(UserProfile, user=current_user)  # Assuming UserProfile model exists
    try:
        existingpayment = get_object_or_404(Payment, pk=payment_id, user=current_user)
        existingpayment.delete()
    except Exception as e:
        print(f"Error deleting payment: {e}")
    return redirect('student_profile', student_id=student.id)






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def record_attendance(request, roomname):
    room = Rooms.objects.get(roomname=roomname)
    students = Student.objects.filter(rooms=room).order_by('full_name')
    
    if request.method == 'POST':
        # Get the date input from the form
        date = request.POST.get('attendance_date')
        # Convert the date string to a datetime object
        date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        
        # Loop through each student and record attendance
        for student in students:
            attended = request.POST.get(f'student_{student.id}', False)
            # Create or update attendance record
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                room=room,
                date=date
            )
            attendance.attended = attended
            attendance.save()

        return redirect('room_detail', roomname=roomname)

    context = {
        'roomname': roomname,
        'students': students,
    }
    return render(request, 'home/record_attendance.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_attendance(request, roomname):
    room = get_object_or_404(Rooms, roomname=roomname)
    students = Student.objects.filter(rooms=room)
    date = request.POST.get('attendance_date')
    selected_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
    print(selected_date)
    attendance_records = Attendance.objects.filter(room=room, date=selected_date)
    print(attendance_records)
    

    context = {
        'roomname': roomname,
        'students': students,
        'selected_date': selected_date,
        'attendance_records': attendance_records
    }

    return render(request, 'home/edit_attendance.html', context)


def saveeditattendance(request, roomname, date):
    room = get_object_or_404(Rooms, roomname=roomname)
    students = Student.objects.filter(rooms=room)
    if request.method == 'POST':
        for student in students:
            attended = request.POST.get(f'student_{student.id}', False)
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                room=room,
                date=date
            )
            attendance.attended = attended
            attendance.save()

        return redirect('room_detail', roomname=roomname)





def bulk_upload_students(request):
    current_user=request.user
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the uploaded CSV file
            uploaded_file = request.FILES['file']
            # Assuming CSV file has 'full_name', 'email', 'phone_number', 'address' fields
            # You may need to adjust this based on your CSV format
            students_data = [line.decode('utf-8').strip().split(',') for line in uploaded_file]
            for data in students_data:
                full_name, email, school, class_level, phone_number, father_name, father_phone, mother_name, mother_phone, address = data
                student = Student.objects.create(
                    user=current_user,
                    full_name=full_name,
                    email=email,
                    school=school,
                    class_level=class_level,
                    phone_number=phone_number,
                    father_name=father_name,
                    father_phone=father_phone,
                    mother_name=mother_name,
                    mother_phone=mother_phone,
                    address=address,
                )
                # You can add more fields as needed
            return redirect('bulk_upload_success')
    else:
        form = BulkUploadForm()
    return render(request, 'home/bulk_upload.html', {'form': form})

def bulk_upload_success(request):
    return render(request, 'home/bulk_upload_success.html')