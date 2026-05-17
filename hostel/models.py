from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator



# ================= STUDENT PROFILE =================
class Student(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    room_no = models.CharField(max_length=20, blank=True)
    hostel_id = models.CharField(max_length=20, unique=True, blank=True)

    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="Enter valid 10 digit number"
    )

    student_phone = models.CharField(
        max_length=10,
        validators=[phone_validator]
    )

    parent_phone = models.CharField(
        max_length=10,
        validators=[phone_validator]
    )

    GENDER_CHOICES = [
        ('BOYS', 'Boys'),
        ('GIRLS', 'Girls'),
    ]

    DEPARTMENT_CHOICES = [
        ('CSE', 'CSE'),
        ('ENTC', 'ENTC'),
        ('MECH', 'MECH'),
        ('CIVIL', 'CIVIL'),
        ('ECE', 'ECE'),
    ]

    CLASS_CHOICES = [
        ('FY', 'FY'),
        ('SY', 'SY'),
        ('TY', 'TY'),
        ('BE', 'BE'),
    ]

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    department = models.CharField(
        max_length=10,
        choices=DEPARTMENT_CHOICES
    )

    student_class = models.CharField(
        max_length=5,
        choices=CLASS_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ================= SAVE =================
    def save(self, *args, **kwargs):

        # ================= HOSTEL ID =================
        if not self.hostel_id:

            last_student = Student.objects.order_by('-id').first()

            if last_student and last_student.hostel_id:
                num = int(
                    last_student.hostel_id.replace('HST', '')
                ) + 1
            else:
                num = 1

            self.hostel_id = f"HST{num:03d}"

        # ================= FLOOR MAP =================
        class_floors = {
            'FY': [0, 1],
            'SY': [2],
            'TY': [3],
            'BE': [4],
        }

        # ================= AUTO ROOM =================
        if not self.room_no:

            floors = class_floors[self.student_class]

            room_list = []

            for floor in floors:

                blocks = [
                    [1, 2, 3, 4],
                    [5, 6, 7, 8],
                    [9],
                    [10],
                    [11, 12, 13, 14],
                    [15, 16, 17, 18],
                ]

                for block_index, block in enumerate(blocks, start=1):

                    # ✅ PREFIX
                    prefix = "B" if self.gender == "BOYS" else "G"

                    block_code = f"{floor}{block_index:02d}"

                    for room in block:

                        room_code = f"{prefix}{block_code}-{room}"

                        room_list.append(room_code)

            # ================= ROOM LIMIT =================
            if self.gender == "GIRLS":
                room_list = room_list[:86]

            if self.gender == "BOYS":
                room_list = room_list[:90]

            # ================= AUTO ASSIGN =================
            for room in room_list:

                count = Student.objects.filter(
                    gender=self.gender,
                    room_no=room
                ).count()

                if count < 3:
                    self.room_no = room
                    break

            if not self.room_no:
                raise ValidationError("No room available")

        # ================= MAX 3 STUDENTS =================
        existing = Student.objects.filter(
            gender=self.gender,
            room_no=self.room_no
        ).exclude(id=self.id).count()

        if existing >= 3:
            raise ValidationError("Room already full")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

# ================= LEAVE REQUEST =================
class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="leaves")

    from_date = models.DateField()
    to_date = models.DateField()

    room_no = models.CharField(max_length=10)
    student_phone = models.CharField(max_length=15)
    parent_phone = models.CharField(max_length=15)

    place = models.CharField(max_length=100)
    reason = models.TextField()

    # Multi-level approval
    cc_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    hod_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rector_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    final_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.username} | {self.from_date} → {self.to_date}"


# ================= FEES =================
class Fee(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="fees"
    )

    total_amount = models.PositiveIntegerField()

    paid_amount = models.PositiveIntegerField(default=0)

    pending_amount = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    paid_on = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):

        # ================= PENDING =================
        self.pending_amount = self.total_amount - self.paid_amount

        # ================= STATUS =================
        if self.pending_amount <= 0:
            self.status = "Paid"
            self.pending_amount = 0

        elif self.paid_amount > 0:
            self.status = "Partial"

        else:
            self.status = "Pending"

        # ================= PAID DATE =================
        if self.status == "Paid":
            self.paid_on = now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.username} - ₹{self.total_amount}"


# ================= OUTING =================
class Outing(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="outings")

    out_time = models.DateTimeField()
    in_time = models.DateTimeField(null=True, blank=True)

    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-out_time']

    def __str__(self):
        return f"{self.student.user.username} | Out: {self.out_time}"

# ================= ATTENDANCE =================
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance")

    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.user.username} | {self.date} | {self.status}"


# ================= FEEDBACK =================
class Feedback(models.Model):
    FEEDBACK_TYPE = [
        ('Mess', 'Mess'),
        ('Hostel', 'Hostel'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")

    type = models.CharField(max_length=20, choices=FEEDBACK_TYPE)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type}"