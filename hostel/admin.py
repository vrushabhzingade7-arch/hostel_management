from django.contrib import admin
from .models import Student, LeaveRequest, Fee, Attendance, Outing, Feedback

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


# ================= STUDENT IMPORT =================
class StudentResource(resources.ModelResource):

    username = fields.Field(column_name='username')
    password = fields.Field(column_name='password')
    email = fields.Field(column_name='email')

    student_phone = fields.Field(column_name='student_phone')
    parent_phone = fields.Field(column_name='parent_phone')

    department = fields.Field(column_name='department')
    student_class = fields.Field(column_name='student_class')
    gender = fields.Field(column_name='gender')

    class Meta:
        model = Student

        fields = (
            'username',
            'password',
            'email',
            'student_phone',
            'parent_phone',
            'department',
            'student_class',
            'gender',
        )

        import_id_fields = ()
        skip_unchanged = True
        report_skipped = False

    # ================= CREATE USER =================
    def before_import_row(self, row, **kwargs):

        username = str(row['username']).strip()
        password = str(row['password']).strip()
        email = str(row['email']).strip()

        # skip duplicate username
        if User.objects.filter(username=username).exists():
            return

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        row['user'] = user.id

        del row['username']
        del row['password']
        del row['email']


# ================= STUDENT ADMIN =================
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

    readonly_fields = (
        'hostel_id',
        'room_no'
    )


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
        'total_amount',
        'paid_amount',
        'pending_amount',
        'status',
        'paid_on',
        'created_at'
    )


# ================= ATTENDANCE =================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'date',
        'status'
    )


# ================= OUTING =================
@admin.register(Outing)
class OutingAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'out_time',
        'in_time'
    )


# ================= FEEDBACK =================
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'type',
        'message',
        'created_at'
    )