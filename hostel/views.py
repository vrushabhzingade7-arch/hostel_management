from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from django.db.models import Count, Sum

from .models import Student, LeaveRequest, Attendance, Feedback, Fee, Outing
import csv
from django.http import HttpResponse


# ================= HOME =================
def user_login(request):
    return render(request, 'index.html')


# ================= ADMIN LOGIN =================
@never_cache
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # Allow admin + CC + HOD + Rector
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')

    return render(request, 'admin_login.html')


# ================= STUDENT LOGIN =================
@never_cache
def student_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)

            # ✅ SAFE CHECK
            if Student.objects.filter(user=user).exists():
                return redirect('student_dashboard')
            else:
                return render(request, 'error.html', {
                    'message': 'Student profile not found'
                })

    return render(request, 'student_login.html')

# ================= LOGOUT =================
@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


# ================= ADMIN DASHBOARD =================
@login_required
def admin_dashboard(request):
    total_students = Student.objects.count()
    today = now().date()

    present_students = Attendance.objects.filter(
        date=today,
        status="Present"
    ).count()

    absent_students = total_students - present_students

    return render(request, 'admin_dashboard.html', {
        'total_students': total_students,
        'present_students': present_students,
        'absent_students': absent_students
    })


# ================= STUDENT DASHBOARD =================
@login_required
def student_dashboard(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return render(request, 'error.html', {
            'message': 'Student profile not created'
        })

    return render(request, 'student_dashboard.html', {'student': student})


# ================= APPLY LEAVE =================
@login_required

def apply_leave(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return redirect('student_dashboard')

    if request.method == "POST":
        LeaveRequest.objects.create(
            student=student,
            from_date=request.POST.get('from_date'),
            to_date=request.POST.get('to_date'),
            reason=request.POST.get('reason'),
            place=request.POST.get('place'),

            room_no=student.room_no,
            student_phone=student.student_phone,
            parent_phone=student.parent_phone,
        )
        return redirect('leave_status')  # ✅ INSIDE IF

    return render(request, 'apply_leave.html')


# ================= LEAVE STATUS =================
@login_required
def leave_status(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return redirect('student_dashboard')

    leaves = LeaveRequest.objects.filter(student=student)
    return render(request, 'leave_status.html', {'leaves': leaves})


# ================= ADMIN LEAVE =================
from django.http import HttpResponse

@login_required
def leave_requests(request):
    try:
        dept = request.GET.get('dept')
        cls = request.GET.get('cls')

        # ================= STEP 1 =================
        if not dept:
            departments = [choice[0] for choice in Student.DEPARTMENT_CHOICES]
            return render(request, 'leave_departments.html', {
                'departments': departments
            })

        # ================= STEP 2 =================
        if dept and not cls:
            classes = [choice[0] for choice in Student.CLASS_CHOICES]

            return render(request, 'leave_classes.html', {
                'classes': classes,
                'dept': dept
            })

        # ================= STEP 3 =================
        leaves = LeaveRequest.objects.filter(
            student__department=dept,
            student__student_class=cls
        )

        # ================= ROLE FILTER =================
        if request.user.groups.filter(name='HOD').exists():
            leaves = leaves.filter(cc_status="Approved")

        elif request.user.groups.filter(name='RECTOR').exists():
            leaves = leaves.filter(hod_status="Approved")

       # ================= SAFE GROUPS =================
        groups = list(request.user.groups.values_list('name', flat=True)) if request.user.is_authenticated else []

       # ✅ ADD THESE
        is_cc = 'CC' in groups
        is_hod = 'HOD' in groups
        is_rector = 'RECTOR' in groups

        return render(request, 'leave_requests.html', {
            'leaves': leaves,
            'dept': dept,
            'cls': cls,
            'groups': groups,
            'readonly': request.user.is_superuser,

            # ✅ NEW FLAGS
            'is_cc': is_cc,
            'is_hod': is_hod,
            'is_rector': is_rector,
    })

    except Exception as e:
        return HttpResponse(f"<h1>ERROR:</h1><pre>{e}</pre>")
# ================= APPROVAL =================
@login_required
def approve_leave(request, leave_id, role, action):

    # ❌ SUPERUSER CANNOT MODIFY
    if request.user.is_superuser:
        return redirect('leave_requests')

    leave = get_object_or_404(LeaveRequest, id=leave_id)

    # ❌ Block students
    if Student.objects.filter(user=request.user).exists():
        return redirect('student_dashboard')

    # ================= CC =================
    if request.user.groups.filter(name='CC').exists() and role == "cc":
        leave.cc_status = action

        # 🔴 IF CC REJECTS → FINAL REJECTED
        if action == "Rejected":
            leave.final_status = "Rejected"

    # ================= HOD =================
    elif request.user.groups.filter(name='HOD').exists() and role == "hod" and leave.cc_status == "Approved":
        leave.hod_status = action

        # 🔴 IF HOD REJECTS → FINAL REJECTED
        if action == "Rejected":
            leave.final_status = "Rejected"

    # ================= RECTOR =================
    elif request.user.groups.filter(name='RECTOR').exists() and role == "rector" and leave.hod_status == "Approved":
        leave.rector_status = action

        # ✅ FINAL DECISION BY RECTOR
        if action == "Approved":
            leave.final_status = "Approved"
        else:
            leave.final_status = "Rejected"

    leave.save()
    # get dept & class from POST
    dept = request.POST.get('dept')
    cls = request.POST.get('cls')

    

# ✅ stay on same page
    return redirect(f'/leave_requests/?dept={dept}&cls={cls}')
    
# ================= ATTENDANCE =================
@login_required
def mark_attendance(request):

    gender = request.GET.get('gender')

    if not gender:
        return render(request, 'attendance_gender.html')

    # ✅ FIX CASE
    gender = gender.upper()

    students = Student.objects.filter(gender=gender)
    today = now().date()

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.id}")

            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=today,
                    defaults={'status': status}
                )

        return redirect('admin_dashboard')

    return render(request, 'mark_attendance.html', {
        'students': students,
        'gender': gender
    })

# ================= ROOM INFO =================
@login_required
def room_info(request):

    gender = request.GET.get('gender')

    # ================= SELECT GENDER PAGE =================
    if not gender:
        return render(request, 'room_gender_select.html')

    # ================= FILTER STUDENTS =================
    students = Student.objects.filter(gender=gender).order_by('room_no')

    # ================= ROOM COUNT =================
    rooms = (
        Student.objects
        .filter(gender=gender)
        .exclude(room_no="")
        .values('room_no')
        .annotate(total=Count('id'))
        .order_by('room_no')
    )

    # total hostel rooms
    if gender == "BOYS":
        total_rooms = 90
    else:
        total_rooms = 86

    # common calculation
    filled_rooms = sum(1 for r in rooms if r['total'] >= 3)
    vacant_rooms = total_rooms - len(rooms)

    return render(request, 'room_info.html', {
        'students': students,
        'rooms': rooms,
        'total_rooms': total_rooms,
        'filled_rooms': filled_rooms,
        'vacant_rooms': vacant_rooms,
        'gender': gender,
    })


# ================= UPDATE ROOM =================
@login_required
def update_room(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        student.room_no = request.POST.get('room_no')
        student.save()
        return redirect('room_info')

    return render(request, 'update_room.html', {'student': student})


# ================= STUDENT ROOM =================
@login_required
def student_room(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return render(request, 'error.html', {
            'message': 'Student profile not created.'
        })

    return render(request, 'student_room.html', {'student': student})


# ================= FEES (STUDENT) =================
@login_required
def fees_student(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return redirect('student_dashboard')

    fees = Fee.objects.filter(student=student)

    total = fees.aggregate(total=Sum('amount'))['total'] or 0
    paid = fees.filter(status="Paid").aggregate(total=Sum('amount'))['total'] or 0
    pending = fees.filter(status="Pending").aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'fees_student.html', {
        'fees': fees,
        'total': total,
        'paid': paid,
        'pending': pending
    })


# ================= FEES (ADMIN) =================
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def fees_admin(request):
    dept = request.GET.get('dept')
    cls = request.GET.get('cls')

    # ================= STEP 1: DEPARTMENTS =================
    if not dept:
        departments = [choice[0] for choice in Student.DEPARTMENT_CHOICES]
        return render(request, 'fees_departments.html', {
            'departments': departments
        })

    # ================= STEP 2: CLASSES =================
    if dept and not cls:
        classes = [choice[0] for choice in Student.CLASS_CHOICES]
        return render(request, 'fees_classes.html', {
            'classes': classes,
            'dept': dept
        })

    # ================= STEP 3: FEES TABLE =================
    fees = Fee.objects.select_related('student', 'student__user').filter(
        student__department=dept,
        student__student_class=cls
    )

    # ================= CALCULATIONS =================
    total_amount = sum(f.amount for f in fees)
    paid_amount = sum(f.amount for f in fees if f.status == "Paid")
    pending_amount = sum(f.amount for f in fees if f.status == "Pending")

    # ================= UPDATE STATUS =================
    if request.method == "POST":
        fee = get_object_or_404(Fee, id=request.POST.get("fee_id"))
        action = request.POST.get("action")

        fee.status = action

        if action == "Paid":
            fee.paid_on = now()
        else:
            fee.paid_on = None

        fee.save()

        # ✅ stay on same page
        return redirect(f'/fees_admin/?dept={dept}&cls={cls}')

    return render(request, 'fees_admin.html', {
        'fees': fees,
        'dept': dept,
        'cls': cls,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
    })

## ================= OUTING =================
@login_required
def outing_student(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return redirect('student_dashboard')

    outings = Outing.objects.filter(student=student).order_by('-out_time')
    return render(request, 'outing_student.html', {'outings': outings})


@login_required
def mark_out(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return redirect('student_dashboard')

    if not Outing.objects.filter(student=student, in_time__isnull=True).exists():
        Outing.objects.create(student=student, out_time=now())

    return redirect('outing_student')


@login_required
def mark_in(request, outing_id):
    outing = get_object_or_404(Outing, id=outing_id)

    if outing.in_time is None:
        outing.in_time = now()
        outing.save()

    return redirect('outing_student')


@login_required
def outing_admin(request):
    outings = Outing.objects.select_related('student', 'student__user').all().order_by('-out_time')
    return render(request, 'outing_admin.html', {'outings': outings})


# ================= FEEDBACK =================
@login_required
def feedback_submit(request):
    if request.method == "POST":
        Feedback.objects.create(
            user=request.user,
            type=request.POST.get("type"),
            message=request.POST.get("message")
        )
        return redirect('feedback_submit')

    return render(request, 'feedback_submit.html')


@login_required
def feedback_admin(request):
    feedbacks = Feedback.objects.select_related('user').all().order_by('-created_at')
    return render(request, 'feedback_admin.html', {'feedbacks': feedbacks})


import csv
from io import TextIOWrapper
from django.contrib.auth.models import User
from django.contrib import messages


@login_required
def bulk_upload_students(request):
    if request.method == "POST":
        csv_file = request.FILES.get('file')

        if not csv_file:
            messages.error(request, "Please select CSV file")
            return redirect('bulk_upload')

        file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
        reader = csv.DictReader(file_data)

        created = 0

        for row in reader:
            username = row['username']
            password = row['password']

            if User.objects.filter(username=username).exists():
                continue

            user = User.objects.create_user(
                username=username,
                password=password
            )

            Student.objects.create(
                user=user,
                gender=row['gender'].upper(),
                department=row['department'].upper(),
                student_class=row['student_class'].upper(),
                student_phone=row['student_phone'],
                parent_phone=row['parent_phone']
            )

            created += 1

        messages.success(request, f"{created} students uploaded")
        return redirect('admin_dashboard')

    return render(request, 'bulk_upload.html')

# ================= BULK DELETE STUDENTS =================
import csv
from io import TextIOWrapper
from django.contrib import messages
from django.contrib.auth.models import User


@login_required
def bulk_delete_students(request):

    if request.method == "POST":

        csv_file = request.FILES.get('file')

        if not csv_file:
            messages.error(request, "Please upload CSV file")
            return redirect('bulk_delete')

        file_data = TextIOWrapper(csv_file.file, encoding='utf-8')

        reader = csv.DictReader(file_data)

        deleted = 0

        for row in reader:

            username = row['username']

            try:
                user = User.objects.get(username=username)

                # delete user + student
                user.delete()

                deleted += 1

            except User.DoesNotExist:
                continue

        messages.success(request, f"{deleted} students deleted successfully")

        return redirect('admin_dashboard')

    return render(request, 'bulk_delete.html')

# ================= DOWNLOAD ATTENDANCE =================
@login_required
def download_attendance(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)

    # Header
    writer.writerow([
        'Username',
        'Department',
        'Class',
        'Room No',
        'Date',
        'Status'
    ])

    attendance_data = Attendance.objects.select_related(
        'student',
        'student__user'
    ).all().order_by('-date')

    for attendance in attendance_data:
        writer.writerow([
            attendance.student.user.username,
            attendance.student.department,
            attendance.student.student_class,
            attendance.student.room_no,
            attendance.date,
            attendance.status
        ])

    return response