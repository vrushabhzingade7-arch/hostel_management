from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# ================= STUDENT PROFILE =================
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room_no = models.CharField(max_length=10)
    hostel_id = models.CharField(max_length=20, unique=True)

    student_phone = models.CharField(max_length=15)
    parent_phone = models.CharField(max_length=15)

    # ✅ NEW FIELDS
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

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='BOYS')
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES, default='CSE')
    student_class = models.CharField(max_length=5, choices=CLASS_CHOICES, default='FY')

    created_at = models.DateTimeField(auto_now_add=True)


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
        ('Paid', 'Paid'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")

    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    paid_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto set paid date when marked Paid
        if self.status == "Paid" and not self.paid_on:
            self.paid_on = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.username} - ₹{self.amount} ({self.status})"


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