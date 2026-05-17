from django.contrib import admin
from .models import Student, LeaveRequest, Fee, Attendance, Outing, Feedback
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password



# ================= STUDENT =================
class StudentResource(resources.ModelResource):
    username = fields.Field(column_name='username')
    password = fields.Field(column_name='password')

    class Meta:
        model = Student

        exclude = ('id', 'hostel_id', 'room_no')

        import_id_fields = ('username',)

        fields = (
            'username',
            'password',
            'student_phone',
            'parent_phone',
            'department',
            'student_class',
            'gender',
        )

    def before_import_row(self, row, **kwargs):
        username = row['username']
        password = row['password']

        user, created = User.objects.get_or_create(username=username)

        if created:
            user.password = make_password(password)
            user.save()

        row['user'] = user.id


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource

    list_display = (
        'user',
        'hostel_id',
        'gender',
        'department',
        'student_class',
        'room_no'
    )

    readonly_fields = ('hostel_id', 'room_no')

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