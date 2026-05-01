from django.contrib import admin
from .models import Student, LeaveRequest, Fee, Attendance, Outing, Feedback


# ================= STUDENT =================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'hostel_id', 'department', 'student_class', 'room_no')

# ================= LEAVE =================
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'from_date',
        'to_date',
        'cc_status',
        'hod_status',
        'rector_status',
        'final_status'
    )


# ================= FEES =================
@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'amount',
        'status',
        'paid_on',
        'created_at'
    )

# ================= ATTENDANCE =================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')


# ================= OUTING =================
@admin.register(Outing)
class OutingAdmin(admin.ModelAdmin):
    list_display = ('student', 'out_time', 'in_time')


# ================= FEEDBACK =================
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'message', 'created_at')