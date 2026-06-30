from django.db import models
from django.conf import settings
from django.utils import timezone


class AcademicYear(models.Model):
    year = models.CharField(max_length=20, unique=True)
    is_current = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.year

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-start_date']


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='courses_taught', limit_choices_to={'role': 'lecturer'}
    )
    credit_hours = models.PositiveIntegerField(default=3)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='courses')
    semester = models.CharField(max_length=20, choices=[('Semester 1', 'Semester 1'), ('Semester 2', 'Semester 2')])

    def __str__(self):
        return self.code + " - " + self.name

    class Meta:
        ordering = ['code']


class StudentProfile(models.Model):
    YEAR_CHOICES = [(i, 'Year ' + str(i)) for i in range(1, 5)]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile'
    )
    student_id = models.CharField(max_length=20, unique=True)
    year_of_study = models.PositiveIntegerField(choices=YEAR_CHOICES, default=1)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='students')
    date_of_birth = models.DateField(null=True, blank=True)
    enrolled_at = models.DateField(auto_now_add=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.student_id + " - " + self.user.get_full_name()

    @property
    def overall_gpa(self):
        grades = self.grades.all()
        if not grades:
            return 0
        total = sum(g.percentage for g in grades)
        return round(total / len(grades), 2)

    @property
    def risk_level(self):
        gpa = self.overall_gpa
        att = self.attendance_rate
        if gpa < settings.GRADE_ALERT_THRESHOLD or att < settings.ATTENDANCE_ALERT_THRESHOLD:
            if gpa < 40 or att < 60:
                return 'HIGH'
            return 'MEDIUM'
        return 'LOW'

    @property
    def attendance_rate(self):
        records = self.attendance_records.all()
        if not records:
            return 100
        attended = records.filter(status='present').count()
        return round((attended / records.count()) * 100, 1)

    class Meta:
        ordering = ['student_id']


class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return self.student.student_id + " -> " + self.course.code


class Grade(models.Model):
    GRADE_TYPES = [
        ('ASSIGNMENT1', 'Assignment 1'),
        ('ASSIGNMENT2', 'Assignment 2'),
        ('CAT1', 'Continuous Assessment Test 1'),
        ('CAT2', 'Continuous Assessment Test 2'),
        ('FINAL', 'Final Exam'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    grade_type = models.CharField(max_length=20, choices=GRADE_TYPES)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='grades_uploaded'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True)

    @property
    def percentage(self):
        if self.max_score == 0:
            return 0
        return round(float(self.score) / float(self.max_score) * 100, 2)

    @property
    def letter_grade(self):
        p = self.percentage
        if p >= 80:
            return 'A'
        elif p >= 70:
            return 'B'
        elif p >= 60:
            return 'C'
        elif p >= 50:
            return 'D'
        return 'F'

    def __str__(self):
        return self.student.student_id + " | " + self.course.code + " | " + self.grade_type + ": " + str(self.score) + "/" + str(self.max_score)

    class Meta:
        unique_together = ('student', 'course', 'grade_type')
        ordering = ['-uploaded_at']


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='attendance_recorded'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.student.student_id + " | " + self.course.code + " | " + str(self.date) + " | " + self.status

    class Meta:
        unique_together = ('student', 'course', 'date')
        ordering = ['-date']